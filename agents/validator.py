import sqlglot
from sqlglot import exp


def validate_sql(sql: str) -> str:
    """
    Validate generated SQL before execution.

    Allowed:
        SELECT
        WITH / CTE

    Blocked:
        INSERT
        UPDATE
        DELETE
        DROP
        CREATE
        ALTER
        TRUNCATE
        GRANT
        REVOKE
    """

    # ========================================================
    # 1. BASIC VALIDATION
    # ========================================================

    if not sql or not sql.strip():
        raise ValueError("Generated SQL is empty.")

    sql = sql.strip()

    # Remove accidental Markdown fences
    if sql.startswith("```"):
        sql = sql.replace("```sql", "")
        sql = sql.replace("```postgresql", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

    # ========================================================
    # 2. PARSE SQL
    # ========================================================

    try:
        statements = sqlglot.parse(
            sql,
            read="postgres"
        )
    except Exception as exc:
        raise ValueError(
            f"Invalid PostgreSQL SQL: {exc}"
        ) from exc

    if len(statements) != 1:
        raise ValueError(
            "Only one SQL statement is permitted."
        )

    tree = statements[0]

    # ========================================================
    # 3. BLOCK DANGEROUS SQL OPERATIONS
    # ========================================================

    dangerous_types = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
    )

    for node_type in dangerous_types:

        if tree.find(node_type):

            raise ValueError(
                f"Unsafe SQL detected: "
                f"{node_type.__name__}"
            )

    # ========================================================
    # 4. NORMALIZE SQL
    # ========================================================

    normalized = " ".join(
        sql.upper().split()
    )

    # ========================================================
    # 5. BLOCK TRUNCATE
    # ========================================================

    if normalized.startswith("TRUNCATE"):
        raise ValueError(
            "Unsafe SQL detected: TRUNCATE"
        )

    # ========================================================
    # 6. ONLY SELECT / WITH
    # ========================================================

    if not normalized.startswith(
        ("SELECT ", "WITH ")
    ):
        raise ValueError(
            "Only SELECT/WITH queries are permitted."
        )

    # ========================================================
    # 7. ADDITIONAL SECURITY CHECK
    # ========================================================

    blocked_keywords = (
        "INSERT ",
        "UPDATE ",
        "DELETE ",
        "DROP ",
        "CREATE ",
        "ALTER ",
        "TRUNCATE ",
        "GRANT ",
        "REVOKE ",
    )

    for keyword in blocked_keywords:

        if normalized.startswith(keyword):

            raise ValueError(
                f"Unsafe SQL detected: "
                f"{keyword.strip()}"
            )

    return sql