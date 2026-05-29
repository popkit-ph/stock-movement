"""Central configuration: loads .env and defines paths + DB settings."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Project root = directory containing this file
ROOT = Path(__file__).resolve().parent

# Load environment variables from .env (if present)
load_dotenv(ROOT / ".env")

# ---- Paths --------------------------------------------------------------
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FRONTEND_DIR = ROOT / "frontend"

EXCEL_PATH = RAW_DIR / os.getenv("EXCEL_FILE", "Stock Online_JLC GROUP 2026.xlsx")
JSON_PATH = PROCESSED_DIR / "stock_data.json"
COMPACT_JSON_PATH = PROCESSED_DIR / "stock_data_compact.json"

# ---- Database -----------------------------------------------------------
DB = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "5432")),
    dbname=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
)
DB_SCHEMA = os.getenv("DB_SCHEMA", "stock_online")

# ---- Server -------------------------------------------------------------
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
