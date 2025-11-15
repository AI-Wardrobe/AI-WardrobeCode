
import streamlit as st
import os, glob
from src.db.db import list_items, add_item
from src.vision.tagger import extract_dominant_color, classify_type_from_name
from src.recommender.rules import recommend, Item

st.set_page_config(page_title="AI Closet", page_icon="👕", layout="wide")
st.title("AI Closet — Web Prototype")

# Upload area
images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "images")

with st.sidebar:
    st.header("Upload Clothing")
    upl = st.file_uploader("Add image", type=["png","jpg","jpeg"])
    if upl:
        save_path = os.path.join(images_dir, upl.name)
        with open(save_path, "wb") as f:
            f.write(upl.getbuffer())
        color = extract_dominant_color(save_path)
        itype = classify_type_from_name(upl.name)
        add_item(filename=upl.name, type_=itype, dominant_color=color)
        st.success(f"Saved {upl.name} as {itype} with color {color}")

st.subheader("Current Wardrobe")
rows = list_items(limit=100)
if rows:
    st.dataframe(rows, use_container_width=True)
else:
    st.info("No items yet — upload from the sidebar.")

st.subheader("Get Recommendations")
col1, col2 = st.columns(2)
with col1: temp = st.slider("Temperature (°F)", 30, 100, value=68)
with col2: occasion = st.selectbox("Occasion", ["class","work","casual","formal"])

if st.button("Suggest Outfits"):
    items = [Item(id=r[0], type=r[2] or "unknown", color=r[3] or "rgb(128,128,128)") for r in rows]
    context = {"temp_f": temp, "occasion": occasion}
    recs = recommend(items, context)
    if not recs:
        st.warning("No valid outfits yet. Try uploading at least one top and one bottom.")
    for outfit in recs:
        st.write("— **Outfit** —")
        st.write([f"{i.type} (id={i.id}, {i.color})" for i in outfit])
