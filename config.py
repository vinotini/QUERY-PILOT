import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DATABASE_URL = os.getenv("DATABASE_URL", "")
MAX_SQL_RETRIES = int(os.getenv("MAX_SQL_RETRIES", "3"))
MAX_ROWS = int(os.getenv("MAX_ROWS", "1000"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "6"))

def validate_config():
    missing = []
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not DATABASE_URL:
        missing.append("DATABASE_URL")
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))
