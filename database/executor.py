import pandas as pd
from sqlalchemy import text
from database.connection import engine
from config import MAX_ROWS

def execute_readonly(sql: str):
    with engine.connect() as conn:
        df = pd.read_sql_query(text(sql), conn)
    return df.head(MAX_ROWS) if len(df) > MAX_ROWS else df
