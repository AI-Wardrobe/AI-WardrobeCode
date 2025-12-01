# AI_Closet/src/interface/streamlit_app.py

import os
import sys
import glob
import random
from dataclasses import dataclass

import streamlit as st
from PIL import Image

# ---------- Project root on sys.path ----------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ---------- Project imports ----------
from src.db.db import list_items, add_item
from src.vision.tagger import extract_dominant_color, classify_type_from_name
from src.recommender.rules import recommend  # don't import Item from rules

# ---------- Types ----------
@dataclass
class Item:
    id: int
    filename: str
    type: str
    color: str
    # Extend later if you want:
    # pattern: str | None = None
    # season: str | None = None
    # formality: int | None = None

# ---------- Helpers ----------
ALLOWED_EXTS = {".jpg", ".jpeg", ".png"}

def find_image_path(images_dir: str, filename: str) -> str | None:
    """
    Return a valid local path to the image, trying .jpg/.jpeg/.png.
    Works even if DB has a different extension than the file on disk.
    """
    if not filename:
        return None
    base, ext = os.path.splitext(filename)
    # 1) If full filename exists, use it
    direct = os.path.join(images_dir, filename)
    if os.path.exists(direct):
        return direct
    # 2) Try other allowed extensions for same basename
    for e in (ALLOWED_EXTS - {ext.lower()} if ext else ALLOWED_EXTS):
        cand = os.path.join(images_dir, base + e)
        if os.path.exists(cand):
            return cand
    # 3) Last resort: glob basename.*
    for m in glob.glob(os.path.join(images_dir, base + ".*")):
        if os.path.splitext(m)[1].lower() in ALLOWED_EXTS and os.path.exists(m):
            return m
    return None

def rgb_swatch(rgb_str: str, size=(224, 224)) -> Image.Image:
    """
    Create a solid color image from 'rgb(R,G,B)'.
    Falls back to mid-gray on parse errors.
    """
    try:
        s = rgb_str.strip()
        if s.lower().startswith("rgb(") and s.endswith(")"):
            nums = [int(x) for x in s[4:-1].split(",")]
            if len(nums) == 3:
                return Image.new("RGB", size, tuple(nums))
    except Exception:
        pass
    return Image.new("RGB", size, (128, 128, 128))

# ---------- Streamlit page setup ----------
st.set_page_config(page_title="AI Closet", page_icon="👕", layout="wide")
st.title("AI Closet — Web Prototype")

DATA_DIR = os.path.join(ROOT, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# ---------- Sidebar: upload & auto-tag ----------
with st.sidebar:
    st.header("Upload Clothing")
    upl = st.file_uploader("Add image", type=["png", "jpg", "jpeg"])
    if upl is not None:
        save_path = os.path.join(IMAGES_DIR, upl.name)
        with open(save_path, "wb") as f:
            f.write(upl.getbuffer())
        # quick auto-tags
        color = extract_dominant_color(save_path)
        itype = classify_type_from_name(upl.name)
        add_item(filename=upl.name, type_=itype, dominant_color=color)
        st.success(f"Saved {upl.name} as {itype} with color {color}")

# ---------- Current wardrobe ----------
st.subheader("Current Wardrobe")
rows = list_items(limit=200)  # (id, filename, type, dominant_color, pattern, season, formality)
if rows:
    st.dataframe(rows, use_container_width=True)
else:
    st.info("No items yet — upload from the sidebar.")

# ---------- Controls ----------
st.subheader("Get Recommendations")
c1, c2 = st.columns(2)
with c1:
    temp = st.slider("Temperature (°F)", 30, 100, value=68)
with c2:
    occasion = st.selectbox("Occasion", ["class", "work", "casual", "formal"])

# Build items fresh each run (keeps in sync with DB)
items = [
    Item(
        id=r[0],
        filename=r[1],
        type=(r[2] or "unknown"),
        color=(r[3] or "rgb(128,128,128)"),
    )
    for r in rows
]

# ---- Session state for context, results, and regen ----
ctx = {"temp_f": temp, "occasion": occasion}

if "last_ctx" not in st.session_state:
    st.session_state.last_ctx = None
if "regen_seed" not in st.session_state:
    st.session_state.regen_seed = 0
if "recs" not in st.session_state:
    st.session_state.recs = None

# Buttons
b1, b2 = st.columns([1, 1])
with b1:
    run_clicked = st.button("Suggest Outfits")
with b2:
    regen_clicked = st.button("Regenerate")

# We ONLY compute on button clicks (no auto-run on context change)
should_compute = run_clicked or regen_clicked

if should_compute:
    # If context changed since last time and user clicked Suggest,
    # reset the regeneration seed so first result is stable for the new ctx
    if run_clicked and (st.session_state.last_ctx != ctx):
        st.session_state.regen_seed = 0
    elif regen_clicked:
        st.session_state.regen_seed += 1

    st.session_state.last_ctx = ctx

    # Deterministic variety for same (ctx, seed)
    rng = random.Random(hash((ctx["temp_f"], ctx["occasion"], st.session_state.regen_seed)))

    # Compute recommendations
    recs = recommend(items, ctx)  # expects objects with .type and .color

    # Shuffle for variety (stable for same ctx+seed)
    if recs:
        rng.shuffle(recs)
        for outfit in recs:
            rng.shuffle(outfit)

    # Save to session so they persist until next click
    st.session_state.recs = recs

# ---- Render only if we have results in session (after a click) ----
recs = st.session_state.recs
if recs is None:
    st.info("Set temperature/occasion, then click **Suggest Outfits**.")
elif not recs:
    st.warning("No valid outfits yet. Try uploading at least one top and one bottom.")
else:
    for outfit in recs:
        st.write("— **Outfit** —")
        cols = st.columns(len(outfit))
        for idx, it in enumerate(outfit):
            img_path = find_image_path(IMAGES_DIR, getattr(it, "filename", "") or "")
            with cols[idx]:
                if img_path:
                    st.image(img_path, caption=f"{it.type} (id={it.id})")
                else:
                    st.info(f"Showing color swatch (missing image: {getattr(it, 'filename', 'unknown')})")
                    st.image(rgb_swatch(it.color), caption=f"{it.type} (id={it.id})")
