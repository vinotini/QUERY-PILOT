from llm import generate_with_llm


def clean_sql(sql: str) -> str:
    """
    Clean SQL returned by an LLM.

    Removes accidental Markdown code fences and
    surrounding whitespace.
    """

    if not sql:
        raise ValueError("Generated SQL is empty.")

    sql = sql.strip()

    # Remove Markdown code fences
    if sql.startswith("```sql"):
        sql = sql[len("```sql"):].strip()

    elif sql.startswith("```postgresql"):
        sql = sql[len("```postgresql"):].strip()

    elif sql.startswith("```"):
        sql = sql[len("```"):].strip()

    if sql.endswith("```"):
        sql = sql[:-3].strip()

    # Remove accidental trailing semicolon spacing
    sql = sql.strip()

    if not sql:
        raise ValueError("SQL became empty after cleaning.")

    return sql


def generate_sql(
    question: str,
    plan: str,
    schema_context: str
) -> str:
    """
    Generate PostgreSQL SQL using the centralized
    Gemini → Groq fallback system.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not schema_context or not schema_context.strip():
        raise ValueError("Schema context is empty.")

    prompt = f"""
You are an expert PostgreSQL NL2SQL engineer.

Convert the user's natural-language question into
ONE valid PostgreSQL SQL query.

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
STRICT RULES
========================

1. Generate valid PostgreSQL SQL.

2. Use ONLY tables and columns present in the
   provided database schema.

3. Never invent tables.

4. Never invent columns.

5. Use correct JOIN conditions based on the schema.

6. Use WHERE for filtering.

7. Use GROUP BY for aggregation when required.

8. Use ORDER BY when ranking or sorting is requested.

9. Use LIMIT when the user requests a specific number
   of records.

10. Generate READ-ONLY SQL only.

11. Never use:
    INSERT
    UPDATE
    DELETE
    DROP
    CREATE
    ALTER
    TRUNCATE
    GRANT
    REVOKE

12. Return exactly ONE SQL query.

13. Do not explain the query.

14. Do not return Markdown.

15. Do not use ```sql.

========================
OUTPUT
========================

Return ONLY the PostgreSQL SQL query.
"""

    # Gemini → Groq automatic fallback
    sql = generate_with_llm(prompt)

    # Clean LLM response
    sql = clean_sql(sql)

    return sql