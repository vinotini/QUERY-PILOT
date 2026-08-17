from llm import generate_with_llm
from agents.sql_generator import clean_sql


def correct_sql(
    question,
    plan,
    schema_context,
    previous_sql,
    error
):
    """
    Correct a failed PostgreSQL SQL query.

    Uses the centralized LLM router:

        Gemini
          ↓ 429 / error
        Groq GPT-OSS 20B
          ↓ failure
        Groq GPT-OSS 120B
    """

    prompt = f"""
You are an expert PostgreSQL SQL self-correction agent.

The previous SQL query failed during PostgreSQL execution.

Your task is to fix the SQL query using the database error
and the provided schema.

========================
USER QUESTION
========================

{question}

========================
QUERY PLAN
========================

{plan}

========================
DATABASE SCHEMA
========================

{schema_context}

========================
PREVIOUS SQL
========================

{previous_sql}

========================
POSTGRESQL ERROR
========================

{error}

========================
STRICT RULES
========================

1. Return ONLY the corrected PostgreSQL SQL query.

2. Use ONLY tables and columns that exist in the provided schema.

3. Never invent tables.

4. Never invent columns.

5. Correct the SQL based on the PostgreSQL error.

6. Preserve the original meaning of the user's question.

7. Use valid PostgreSQL syntax.

8. The query must be READ-ONLY.

9. Never use:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   CREATE
   TRUNCATE
   GRANT
   REVOKE

10. Do not modify database data or structure.

11. Do not return Markdown.

12. Do not use ```sql.

13. Do not provide explanations.

14. Return exactly one SQL query.

========================
OUTPUT
========================

Return ONLY the corrected PostgreSQL SQL query.
"""

    # ========================================================
    # GEMINI → GROQ FALLBACK
    # ========================================================

    corrected_sql = generate_with_llm(prompt)

    if not corrected_sql:
        raise RuntimeError(
            "LLM returned an empty corrected SQL query."
        )

    # ========================================================
    # CLEAN SQL
    # ========================================================

    corrected_sql = clean_sql(corrected_sql)

    if not corrected_sql:
        raise RuntimeError(
            "SQL cleaning produced an empty query."
        )

    return corrected_sql
