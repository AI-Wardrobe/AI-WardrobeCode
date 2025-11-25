# AI_Closet/src/interface/streamlit_app.py

import os
import sys
from dataclasses import dataclass

import streamlit as st

# --- Make project root importable (…/AI_Closet) ---
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# --- Project imports ---
from src.db.db import list_items, add_item
from src.vision.tagger import extract_dominant_color, classify_type_from_name
from src.recommender.rules import recommend  # NOTE: we do NOT import Item from rules

# --- Local Item type used by UI & recommender ---
@dataclass
class Item:
    id: int
    filename: str
    type: str
    color: str
    # You can extend later: pattern: str | None = None, season: str | None = None, formality: int | None = None

# --- Streamlit page setup ---
st.set_page_config(page_title="AI Closet", page_icon="👕", layout="wide")
st.title("AI Closet — Web Prototype")

# --- Paths ---
DATA_DIR = os.path.join(ROOT, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# --- Sidebar: uploader writes to data/images and inserts DB row ---
with st.sidebar:
    st.header("Upload Clothing")
    upl = st.file_uploader("Add image", type=["png", "jpg", "jpeg"])
    if upl is not None:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        save_path = os.path.join(IMAGES_DIR, upl.name)

        # Save the file
        with open(save_path, "wb") as f:
            f.write(upl.getbuffer())

        # Quick auto-tags
        color = extract_dominant_color(save_path)
        itype = classify_type_from_name(upl.name)

        # Insert DB row
        add_item(filename=upl.name, type_=itype, dominant_color=color)

        st.success(f"Saved {upl.name} as {itype} with color {color}")

# --- Current wardrobe table ---
st.subheader("Current Wardrobe")
rows = list_items(limit=100)  # (id, filename, type, dominant_color, pattern, season, formality)
if rows:
    st.dataframe(rows, use_container_width=True)
else:
    st.info("No items yet — upload from the sidebar.")

# --- Controls for recommendations ---
st.subheader("Get Recommendations")
col1, col2 = st.columns(2)
with col1:
    temp = st.slider("Temperature (°F)", 30, 100, value=68)
with col2:
    occasion = st.selectbox("Occasion", ["class", "work", "casual", "formal"])


# --- Helpers for fallback color swatch ---
from PIL import Image  # local import keeps startup snappy
import glob

ALLOWED_EXTS = {".jpg", ".jpeg", ".png"}

def find_image_path(images_dir: str, filename: str) -> str | None:
    """
    Return a valid path to the image, trying multiple extensions.
    If `filename` already has an extension, try that first;
    otherwise try .jpg/.jpeg/.png. Falls back to glob match.
    """
    base, ext = os.path.splitext(filename or "")
    # 1) Exact match if a path with extension exists
    if ext:
        p = os.path.join(images_dir, filename)
        if os.path.exists(p):
            return p
        # try same basename with different allowed extensions
        for e in ALLOWED_EXTS - {ext.lower()}:
            p = os.path.join(images_dir, base + e)
            if os.path.exists(p):
                return p
    else:
        # 2) No ext provided → try all allowed
        for e in ALLOWED_EXTS:
            p = os.path.join(images_dir, base + e)
            if os.path.exists(p):
                return p

    # 3) Last resort: glob any file with same basename.* then filter by allowed exts
    matches = glob.glob(os.path.join(images_dir, base + ".*"))
    for m in matches:
        if os.path.splitext(m)[1].lower() in ALLOWED_EXTS and os.path.exists(m):
            return m

    return None

def rgb_swatch(rgb_str: str, size=(224, 224)) -> Image.Image:
    """Create a solid color image from an 'rgb(R,G,B)' string."""
    try:
        s = rgb_str.strip()
        if s.lower().startswith("rgb(") and s.endswith(")"):
            nums = [int(x) for x in s[4:-1].split(",")]
            if len(nums) == 3:
                return Image.new("RGB", size, tuple(nums))
    except Exception:
        pass
    # Fallback mid-gray if parsing fails
    return Image.new("RGB", size, (128, 128, 128))


# --- Recommend & render outfits ---
if st.button("Suggest Outfits"):
    # Build UI Items from DB rows
    items = [
        Item(
            id=r[0],
            filename=r[1],
            type=(r[2] or "unknown"),
            color=(r[3] or "rgb(128,128,128)"),
        )
        for r in rows
    ]

    context = {"temp_f": temp, "occasion": occasion}
    recs = recommend(items, context)  # expects objects with .type and .color

    if not recs:
        st.warning("No valid outfits yet. Try uploading at least one top and one bottom.")
    else:
        for outfit in recs:
            st.write("— **Outfit** —")
            cols = st.columns(len(outfit))
            for idx, it in enumerate(outfit):
                img_path = find_image_path(IMAGES_DIR, getattr(it, "filename", "") or "")
                with cols[idx]:
                    if img_path and os.path.exists(img_path):
                        st.image(img_path, caption=f"{it.type} (id={it.id})")
                    else:
                        st.info(f"Showing color swatch (missing image: {getattr(it, 'filename', 'unknown')})")
                        st.image(rgb_swatch(it.color), caption=f"{it.type} (id={it.id})")
