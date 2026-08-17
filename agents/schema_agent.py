def build_schema_prompt(schema_context: str) -> str:
    """
    Build the schema-grounding prompt for the SQL generation agent.

    This function does not call an LLM.
    It only prepares the retrieved RAG schema context.
    """

    if not schema_context or not schema_context.strip():
        raise ValueError(
            "No schema context was retrieved."
        )

    return f"""
You are the Schema Reasoning Agent in an enterprise NL2SQL system.

Your responsibility is to ground the SQL Generator using ONLY
the database schema retrieved by the RAG system.

========================
RETRIEVED DATABASE SCHEMA
========================

{schema_context}

========================
STRICT RULES
========================

1. Use ONLY the tables shown in the retrieved schema.

2. Use ONLY the columns shown in the retrieved schema.

3. Never invent tables.

4. Never invent columns.

5. Do not assume relationships that are not supported
   by the retrieved schema.

6. Do not generate SQL.

7. Do not modify the schema.

8. The SQL Generator must rely on this schema context
   when constructing the final PostgreSQL query.
"""