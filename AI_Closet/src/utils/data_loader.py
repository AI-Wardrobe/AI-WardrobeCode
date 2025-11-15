# src/utils/data_loader.py

import os
import pandas as pd

from src.db.db import add_item, init_db

# Base directory: go up from this file to project root, then into data/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_tags_csv(csv_path: str | None = None) -> pd.DataFrame:
    """
    Load the tags CSV exported from Colab.

    Expected columns (flexible / not all required):
    - filename or image_name
    - type or predicted_type
    - dominant_color or color
    - pattern (optional)
    - season (optional)
    - formality (optional, numeric or string)
    """
    if csv_path is None:
        csv_path = os.path.join(DATA_DIR, "tags.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find CSV at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Normalize column names to lower-case, no spaces
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def sync_items_from_df(df: pd.DataFrame) -> int:
    """
    Take a DataFrame of tagged clothing items and insert them into the DB.

    Returns:
        int: number of rows successfully inserted.
    """
    inserted = 0

    for _, row in df.iterrows():
        # Try multiple possible filename column names
        filename = (
            row.get("filename")
            or row.get("image_name")
            or row.get("file")
        )

        if not isinstance(filename, str) or not filename:
            # Skip rows with no filename
            continue

        # Type/category of clothing
        type_ = row.get("type") or row.get("predicted_type") or None

        # Dominant color
        dominant_color = row.get("dominant_color") or row.get("color") or None

        # Optional fields
        pattern = row.get("pattern") if "pattern" in row else None
        season = row.get("season") if "season" in row else None

        # Convert formality to int if present
        formality = None
        if "formality" in row and pd.notna(row["formality"]):
            try:
                formality = int(row["formality"])
            except (ValueError, TypeError):
                # If it's not convertible, just leave as None
                formality = None

        # Insert into DB via helper from src/db/db.py
        add_item(
            filename=filename,
            type_=type_,
            dominant_color=dominant_color,
            pattern=pattern,
            season=season,
            formality=formality,
            notes=None,
        )
        inserted += 1

    return inserted


def load_and_sync(csv_path: str | None = None) -> int:
    """
    Convenience function:
    - Loads the CSV
    - Inserts rows into DB
    - Returns number of inserted items
    """
    df = load_tags_csv(csv_path)
    count = sync_items_from_df(df)
    return count


if __name__ == "__main__":
    # Example CLI usage:
    # python -m src.utils.data_loader
    init_db()  # ensure DB/schema exists
    num = load_and_sync()
    print(f"Inserted {num} items into wardrobe.db")
