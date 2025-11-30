import os
import ast
import argparse
import pandas as pd

# Project root (.../AI_Closet)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(ROOT, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# Use your existing color extractor
from src.vision.tagger import extract_dominant_color

# ---- Map ImageNet-ish labels to coarse wardrobe types ----
LABEL_MAP = {
    "top": [
        "shirt", "t-shirt", "tee", "sweatshirt", "sweater", "cardigan",
        "hoodie", "jersey", "blouse", "pullover", "pajama", "flannel",
    ],
    "bottom": [
        "jean", "jeans", "trousers", "pants", "slacks", "chinos",
        "shorts", "skirt", "miniskirt", "sarong", "overskirt",
    ],
    "shoes": [
        "sneaker", "running shoe", "boot", "loafer", "Loafer",
        "sandal", "clog", "slipper", "shoe",
    ],
    "outerwear": [
        "coat", "trench coat", "fur coat", "jacket", "parka",
        "windbreaker", "raincoat", "overcoat", "cloak", "stole",
    ],
}

def safe_parse_labels(val) -> list[str]:
    """labels is a string like "['running shoe','clog',...]" -> list[str]."""
    if isinstance(val, list):
        return [str(x) for x in val]
    if isinstance(val, str):
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            pass
        # fallback: comma-split
        return [x.strip() for x in val.split(",") if x.strip()]
    return []

def to_coarse_type(labels: list[str]) -> str:
    """Return one of {top,bottom,shoes,outerwear,unknown} by scanning label text."""
    joined = " ".join(labels).lower()
    for coarse, keys in LABEL_MAP.items():
        for k in keys:
            if k.lower() in joined:
                return coarse
    return "unknown"

def main(in_csv: str, out_csv: str, images_dir: str, compute_color: bool):
    if not os.path.exists(in_csv):
        raise FileNotFoundError(f"Could not find input CSV: {in_csv}")

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    df = pd.read_csv(in_csv, sep=",")
    if "image" not in df.columns or "labels" not in df.columns:
        raise ValueError("CSV must contain 'image' and 'labels' columns.")

    out_rows = []
    missing_images = 0

    for _, row in df.iterrows():
        image_path = str(row["image"])
        labels = safe_parse_labels(row["labels"])
        coarse = to_coarse_type(labels)

        fname = os.path.basename(image_path)  # keep basename only
        local_path = os.path.join(images_dir, fname)

        dom_color = None
        if compute_color and os.path.exists(local_path):
            try:
                dom_color = extract_dominant_color(local_path)
            except Exception:
                dom_color = None
        else:
            if compute_color:
                missing_images += 1

        out_rows.append({
            "filename": fname,
            "type": coarse,
            "dominant_color": dom_color,
            "pattern": None,
            "season": None,
            "formality": None,
        })

    out_df = pd.DataFrame(out_rows, columns=[
        "filename","type","dominant_color","pattern","season","formality"
    ])
    out_df.to_csv(out_csv, index=False)

    print(f"✅ Wrote cleaned tags to: {out_csv}")
    print(f"   Rows: {len(out_df)}")
    if compute_color:
        print(f"   Images missing locally (color skipped): {missing_images}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post-process Colab tags.csv for AI Closet.")
    parser.add_argument("--in", dest="in_csv", default=os.path.join(DATA_DIR, "tags_colab.csv"),
                        help="Input Colab CSV (default: data/tags_colab.csv)")
    parser.add_argument("--out", dest="out_csv", default=os.path.join(DATA_DIR, "tags.csv"),
                        help="Output CSV for app (default: data/tags.csv)")
    parser.add_argument("--images", dest="images_dir", default=IMAGES_DIR,
                        help="Local images dir (default: data/images)")
    parser.add_argument("--no-color", dest="no_color", action="store_true",
                        help="Skip dominant color extraction even if files exist.")
    args = parser.parse_args()

    main(
        in_csv=args.in_csv,
        out_csv=args.out_csv,
        images_dir=args.images_dir,
        compute_color=not args.no_color
    )
