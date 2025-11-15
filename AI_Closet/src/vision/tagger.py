
from typing import Tuple, Dict
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

def extract_dominant_color(image_path: str, k: int = 3) -> str:
    img = Image.open(image_path).convert("RGB").resize((128,128))
    arr = np.array(img).reshape(-1,3)
    km = KMeans(n_clusters=k, n_init="auto").fit(arr)
    centers = km.cluster_centers_.astype(int)
    # Choose the most populous cluster
    labels, counts = np.unique(km.labels_, return_counts=True)
    dominant = centers[labels[np.argmax(counts)]]
    return f"rgb({dominant[0]},{dominant[1]},{dominant[2]})"

# Placeholder for a real classifier; returns coarse type using filename hints.
def classify_type_from_name(filename: str) -> str:
    name = filename.lower()
    if any(k in name for k in ["hoodie","sweater","tee","shirt","top","blouse"]):
        return "top"
    if any(k in name for k in ["jeans","pants","trouser","skirt","short"]):
        return "bottom"
    if any(k in name for k in ["jacket","coat","parka","hoodie"]):
        return "outerwear"
    if any(k in name for k in ["sneaker","shoe","boot"]):
        return "shoes"
    return "unknown"
