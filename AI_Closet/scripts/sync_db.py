import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
 
from src.db.db import init_db
from src.utils.data_loader import load_and_sync


def main():
    # Ensure schema exists
    init_db()
    # Load CSV and insert into DB
    inserted = load_and_sync()
    print(f"✅ Inserted {inserted} items into wardrobe.db")


if __name__ == "__main__":
    main()
