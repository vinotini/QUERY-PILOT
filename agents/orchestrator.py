import time

from config import MAX_SQL_RETRIES
from rag.retriever import SchemaRetriever

from agents.planner import create_plan
from agents.schema_agent import build_schema_prompt
from agents.sql_generator import generate_sql
from agents.validator import validate_sql
from agents.correction import correct_sql
from agents.insight import generate_insights

from database.executor import execute_readonly


class NL2SQLOrchestrator:

    def __init__(self):
        self.retriever = SchemaRetriever()

    def refresh_rag(self):
        """
        Refresh/reload the schema retriever.
        """
        self.retriever.refresh()

    def run(self, question):

        # ====================================================
        # 0. INPUT VALIDATION
        # ====================================================

        if not question or not question.strip():
            raise ValueError(
                "Please enter a question."
            )

        start = time.time()
        trace = []
        errors = []

        # ====================================================
        # 1. PLANNER AGENT
        # ====================================================

        plan = create_plan(question)

        trace.append(
            "1. Planner Agent completed."
        )

        # ====================================================
        # 2. RAG / SCHEMA RETRIEVAL
        # ====================================================

        retrieved = self.retriever.retrieve(question)

        trace.append(
            f"2. RAG retrieved {len(retrieved)} "
            f"schema documents."
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Do NOT send an empty schema to the LLM.
        # ----------------------------------------------------

        if not retrieved:

            raise ValueError(
                "No database schema was retrieved from RAG.\n\n"
                "Please make sure your database schema has been "
                "indexed into Qdrant.\n\n"
                "Run:\n"
                "python scripts/index_database_schema.py"
            )

        # ====================================================
        # 3. FORMAT SCHEMA CONTEXT
        # ====================================================

        schema_context = self.retriever.format_context(
            retrieved
        )

        if not schema_context or not schema_context.strip():

            raise ValueError(
                "Database schema context is empty.\n\n"
                "The RAG retriever returned documents, but they "
                "contained no usable schema information.\n\n"
                "Please check your Qdrant schema indexing."
            )

        trace.append(
            "2.1 RAG schema context successfully created."
        )

        # ====================================================
        # 4. SCHEMA AGENT
        # ====================================================

        schema_prompt = build_schema_prompt(
            schema_context
        )

        if not schema_prompt or not schema_prompt.strip():

            raise ValueError(
                "Schema Agent returned an empty schema prompt."
            )

        trace.append(
            "3. Schema Agent grounded the SQL context."
        )

        # ====================================================
        # 5. SQL GENERATION
        # ====================================================

        sql = generate_sql(
            question,
            plan + "\n" + schema_prompt,
            schema_context
        )

        # ----------------------------------------------------
        # Validate LLM response BEFORE SQLGlot
        # ----------------------------------------------------

        if not sql or not sql.strip():

            raise ValueError(
                "SQL Generator returned an empty response."
            )

        sql = sql.strip()

        # Remove Markdown SQL fences if the LLM returns them.
        if sql.startswith("```sql"):
            sql = sql[6:]

        elif sql.startswith("```SQL"):
            sql = sql[6:]

        if sql.endswith("```"):
            sql = sql[:-3]

        sql = sql.strip()

        # ----------------------------------------------------
        # Detect schema-insufficient response
        # ----------------------------------------------------

        if sql.upper() == "SCHEMA_INSUFFICIENT":

            raise ValueError(
                "The retrieved database schema is insufficient "
                "to generate this SQL query."
            )

        # ----------------------------------------------------
        # Prevent explanatory LLM text from reaching SQLGlot
        # ----------------------------------------------------

        invalid_prefixes = (
            "I cannot",
            "I can't",
            "I'm unable",
            "I am unable",
            "Sorry",
            "Unable to generate",
            "Cannot generate",
        )

        if sql.lower().startswith(
            tuple(prefix.lower() for prefix in invalid_prefixes)
        ):

            raise ValueError(
                "The SQL Generator returned an explanation "
                "instead of SQL.\n\n"
                "This usually means the retrieved schema "
                "is insufficient."
            )

        # ====================================================
        # 6. SQL VALIDATION
        # ====================================================

        validate_sql(sql)

        trace.append(
            "4. SQL Generator created validated SQL."
        )

        # ====================================================
        # 7. SQL EXECUTION + SELF CORRECTION
        # ====================================================

        result = None

        for attempt in range(MAX_SQL_RETRIES + 1):

            try:

                result = execute_readonly(sql)

                trace.append(
                    f"5. PostgreSQL execution succeeded "
                    f"on attempt {attempt + 1}."
                )

                break

            except Exception as exc:

                errors.append(
                    f"Attempt {attempt + 1}: "
                    f"{type(exc).__name__}: {exc}"
                )

                # --------------------------------------------
                # No retries remaining
                # --------------------------------------------

                if attempt >= MAX_SQL_RETRIES:

                    raise

                trace.append(
                    f"5.{attempt + 1}. SQL execution failed. "
                    "Correction Agent invoked."
                )

                # --------------------------------------------
                # SELF CORRECTION
                # --------------------------------------------

                sql = correct_sql(
                    question,
                    plan,
                    schema_context,
                    sql,
                    str(exc)
                )

                if not sql or not sql.strip():

                    raise ValueError(
                        "Correction Agent returned empty SQL."
                    )

                sql = sql.strip()

                # Remove Markdown fences
                if sql.startswith("```sql"):
                    sql = sql[6:]

                elif sql.startswith("```SQL"):
                    sql = sql[6:]

                if sql.endswith("```"):
                    sql = sql[:-3]

                sql = sql.strip()

                # Detect insufficient schema
                if sql.upper() == "SCHEMA_INSUFFICIENT":

                    raise ValueError(
                        "Correction Agent could not generate "
                        "SQL because the schema is insufficient."
                    )

                # Validate corrected SQL
                validate_sql(sql)

                trace.append(
                    f"5.{attempt + 1}. Corrected SQL validated."
                )

        # ====================================================
        # 8. INSIGHT AGENT
        # ====================================================

        insights = generate_insights(
            question,
            result
        )

        trace.append(
            "6. Insight Agent completed."
        )

        # ====================================================
        # 9. EXECUTION TIME
        # ====================================================

        trace.append(
            f"7. Total time: "
            f"{time.time() - start:.2f}s."
        )

        # ====================================================
        # 10. FINAL RESPONSE
        # ====================================================

        return {
            "plan": plan,
            "retrieved": retrieved,
            "schema_context": schema_context,
            "sql": sql,
            "result": result,
            "insights": insights,
            "trace": "\n".join(trace),
            "errors": (
                "\n".join(errors)
                if errors
                else "No execution errors."
            )
        }