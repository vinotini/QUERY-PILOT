from database.schema import get_schema, get_relationships


def build_documents():
    """
    Build RAG documents from the PostgreSQL database schema.

    Each table becomes one document containing:
    - Table name
    - Column names
    - Data types
    - Foreign-key relationships
    """

    # =========================================================
    # 1. GET DATABASE SCHEMA
    # =========================================================

    rows = get_schema()

    if not rows:
        raise RuntimeError(
            "Database schema is empty.\n\n"
            "get_schema() returned no tables or columns.\n"
            "Check your PostgreSQL connection and database."
        )

    print(
        f"[SCHEMA] Found {len(rows)} column definitions."
    )

    # =========================================================
    # 2. GET TABLE RELATIONSHIPS
    # =========================================================

    relationships = get_relationships()

    if relationships is None:
        relationships = []

    print(
        f"[SCHEMA] Found {len(relationships)} relationships."
    )

    # =========================================================
    # 3. BUILD RELATIONSHIP MAP
    # =========================================================

    rel_map = {}

    for rel in relationships:

        table_name = rel.get("table_name")
        column_name = rel.get("column_name")
        foreign_table = rel.get("foreign_table_name")
        foreign_column = rel.get("foreign_column_name")

        # Skip incomplete relationship records
        if not all([
            table_name,
            column_name,
            foreign_table,
            foreign_column
        ]):
            continue

        relationship_text = (
            f"{column_name} -> "
            f"{foreign_table}.{foreign_column}"
        )

        rel_map.setdefault(
            table_name,
            []
        ).append(
            relationship_text
        )

    # =========================================================
    # 4. GROUP COLUMNS BY TABLE
    # =========================================================

    grouped = {}

    for row in rows:

        table_name = row.get("table_name")
        column_name = row.get("column_name")
        data_type = row.get("data_type")

        if not table_name or not column_name:
            continue

        column_text = (
            f"{column_name} "
            f"({data_type or 'unknown'})"
        )

        grouped.setdefault(
            table_name,
            []
        ).append(
            column_text
        )

    # =========================================================
    # 5. BUILD RAG DOCUMENTS
    # =========================================================

    documents = []

    for table, columns in grouped.items():

        # Basic table + columns information
        content = (
            f"TABLE: {table}. "
            f"COLUMNS: {', '.join(columns)}."
        )

        # Add relationships if available
        if table in rel_map:

            content += (
                " RELATIONSHIPS: "
                + "; ".join(
                    rel_map[table]
                )
                + "."
            )

        document = {
            "id": table,
            "table": table,
            "text": content
        }

        documents.append(
            document
        )

    # =========================================================
    # 6. FINAL VALIDATION
    # =========================================================

    if not documents:

        raise RuntimeError(
            "Schema was successfully retrieved from the "
            "database, but no RAG documents could be created."
        )

    print(
        f"[RAG] Created "
        f"{len(documents)} schema documents."
    )

    # =========================================================
    # 7. DEBUG OUTPUT
    # =========================================================

    for document in documents:

        print(
            f"[RAG] {document['table']}: "
            f"{document['text']}"
        )

    return documents