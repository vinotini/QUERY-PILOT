from database.schema import get_schema, get_relationships


def build_documents():

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

    # =========================================================
    # 2. GET TABLE RELATIONSHIPS
    # =========================================================

    relationships = get_relationships()

    if relationships is None:
        relationships = []

    print(
        f"[SCHEMA] Found {len(rows)} column definitions."
    )

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

        if not all([
            table_name,
            column_name,
            foreign_table,
            foreign_column
        ]):
            continue

        rel_map.setdefault(
            table_name,
            []
        ).append(
            f"{column_name} -> "
            f"{foreign_table}.{foreign_column}"
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

        grouped.setdefault(
            table_name,
            []
        ).append(
            f"{column_name} ({data_type or 'unknown'})"
        )

    # =========================================================
    # 5. BUILD RAG DOCUMENTS
    # =========================================================

    documents = []

    for table, columns in grouped.items():

        content = (
            f"TABLE {table}. "
            f"COLUMNS: {', '.join(columns)}."
        )

        if table in rel_map:

            content += (
                " RELATIONSHIPS: "
                + "; ".join(rel_map[table])
                + "."
            )

        documents.append(
            {
                "id": table,
                "table": table,
                "text": content
            }
        )

    # =========================================================
    # 6. FINAL VALIDATION
    # =========================================================

    if not documents:

        raise RuntimeError(
            "Schema was retrieved from the database, "
            "but no RAG documents could be created."
        )

    print(
        f"[RAG] Created {len(documents)} schema documents."
    )

    for document in documents:

        print(
            f"[RAG] {document['table']}: "
            f"{document['text']}"
        )

    return documents