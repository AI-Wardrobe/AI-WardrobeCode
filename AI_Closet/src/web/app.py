import streamlit as st
import pandas as pd
from PIL import Image
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))  # go up 2 levels
sys.path.append(PROJECT_ROOT)

# Now the import works because src is in the Python path
from src.recommender.rules import recommend as recommend_outfit, Item


# ---------------------------------------------------
# Load Data
# ---------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/cleaned_tags.csv")

df = load_data()


# ---------------------------------------------------
# Convert DataFrame into Item objects for recommender
# ---------------------------------------------------
def df_to_items(df):
    items = []
    for _, row in df.iterrows():
        items.append(
            Item(
                type=row["category"],   # category → type
                color=row["color"],
                image_path=row["image_path"],
                tags=row["tags"]
            )
        )
    return items





# ---------------------------------------------------
# Streamlit UI
# ---------------------------------------------------
st.title("AI Closet – Outfit Recommendation System")

# Sidebar filters
st.sidebar.header("Filters")
weather = st.sidebar.selectbox("Weather:", ["Any", "Hot", "Cold", "Mild"])
occasion = st.sidebar.selectbox("Occasion:", ["Any", "Casual", "Formal", "Sport"])

st.subheader("Your Wardrobe Items")

# Select one item
selected_item = st.selectbox("Choose an item you want to style:", df["category"].unique())

# Display image of selected item
image_path = df.loc[df["category"] == selected_item, "image_path"].values[0]
if os.path.exists(image_path):
    st.image(Image.open(image_path), width=250)


# ---------------------------------------------------
# Generate Recommendations
# ---------------------------------------------------
if st.button("Recommend Outfit"):

    with st.spinner("Thinking..."):

        # Convert whole wardrobe into Item objects
        items_list = df_to_items(df)

        # Map weather → approximate temperature
        temp_lookup = {
            "Cold": 55,
            "Hot": 85,
            "Mild": 70,
            "Any": 70,
        }

        context = {"temp_f": temp_lookup[weather]}

        # Run the recommendation engine
        outfits = recommend_outfit(items_list, context)

    st.subheader("Suggested Outfits:")

    # Display results
    for outfit in outfits:
        st.write("---")

        for item in outfit:
            # item is an Item(dataclass)
            # Using category to find the item (assuming no duplicates)
            df_row = df[df["category"] == item.type].iloc[0]

            st.write(f"• **{df_row['category']}** ({item.type}, {item.color})")

            if os.path.exists(df_row["image_path"]):
                st.image(df_row["image_path"], width=200)

