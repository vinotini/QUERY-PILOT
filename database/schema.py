from sqlalchemy import text
from database.connection import engine


def get_schema():
    """
    Retrieve all tables and columns from the public PostgreSQL schema.
    """

    query = text("""
        SELECT
            table_schema,
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)

    try:
        with engine.connect() as conn:
            rows = conn.execute(query).mappings().all()

        schema = [dict(row) for row in rows]

        print(
            f"[DATABASE] Found {len(schema)} column definitions."
        )

        if not schema:
            print(
                "[DATABASE] WARNING: No tables/columns found "
                "in the public schema."
            )

        return schema

    except Exception as exc:
        raise RuntimeError(
            f"Failed to retrieve database schema: {exc}"
        ) from exc


def get_relationships():
    """
    Retrieve all foreign-key relationships from the public schema.
    """

    query = text("""
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc

        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema

        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema

        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'

        ORDER BY
            tc.table_name,
            kcu.column_name
    """)

    try:
        with engine.connect() as conn:
            rows = conn.execute(query).mappings().all()

        relationships = [dict(row) for row in rows]

        print(
            f"[DATABASE] Found "
            f"{len(relationships)} foreign-key relationships."
        )

        return relationships

    except Exception as exc:
        raise RuntimeError(
            f"Failed to retrieve database relationships: {exc}"
        ) from exc