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
