from sqlalchemy import create_engine, text
from config import DATABASE_URL, validate_config

validate_config()

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

def test_connection():
    with engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar_one()
