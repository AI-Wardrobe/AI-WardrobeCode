
import os
import sqlite3
from dotenv import load_dotenv

DEFAULT_DB = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "metadata", "wardrobe.db"))

def get_conn(db_path: str | None = None):
    return sqlite3.connect(db_path or DEFAULT_DB)

def init_db(db_path: str | None = None):
    from pathlib import Path
    dbp = db_path or DEFAULT_DB
    Path(os.path.dirname(dbp)).mkdir(parents=True, exist_ok=True)
    with get_conn(dbp) as conn:
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    print(f"Initialized DB at {dbp}")

def add_item(filename: str, type_: str | None = None, dominant_color: str | None = None, pattern: str | None = None, season: str | None = None, formality: int | None = None, notes: str | None = None):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO items(filename, type, dominant_color, pattern, season, formality, notes) VALUES(?,?,?,?,?,?,?)",
            (filename, type_, dominant_color, pattern, season, formality, notes)
        )
        conn.commit()
        return cur.lastrowid

def list_items(limit: int = 50):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, filename, type, dominant_color, pattern, season, formality FROM items ORDER BY id DESC LIMIT ?", (limit,))
        return cur.fetchall()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Initialize the SQLite database")
    args = parser.parse_args()
    if args.init:
        init_db()
