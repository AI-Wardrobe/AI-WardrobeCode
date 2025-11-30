<div align="center">
  AI Closet
An Intelligent Outfit Recommendation System

Created by: Jaylyn Lowes, ShaKaylah Macklin, Christopher McDonald, and Brianna Moore
VSU — Intro to AI 

</div>
Overview

AI Closet is an intelligent outfit recommendation system that helps users upload clothing items, classify them using AI, store metadata in a database, and receive personalized outfit suggestions based on weather, occasion, and clothing compatibility.

The system integrates:

Google Colab AI Model (ImageNet-based feature extraction)

Image processing + dominant color extraction

SQLite database pipeline

Recommendation rules engine

Streamlit Web Interface

Data cleaning + preprocessing scripts

This project demonstrates end-to-end AI system design, including ML inference, data engineering, intelligent decision-making, and UI integration.

**Features** <br>
🔹 1. AI-Powered Clothing Tagging (Google Colab)

Uses ResNet50 pretrained on ImageNet

Extracts top 5 predicted labels per image

Saves predictions to tags_colab.csv

🔹 2. Automated Clothing Metadata Cleaning

Script:

python -m src.utils.colab_postprocess


Produces tags.csv formatted as:

filename	type	dominant_color	pattern	season	formality
🔹 3. SQLite Database Integration

Load metadata into the DB:

python scripts/sync_db.py

🔹 4. Streamlit Web UI

Run the app:

streamlit run src/interface/streamlit_app.py


**User Features:**

Upload clothing images

Auto-classify type + color

View your wardrobe

Get outfit recommendations

Rule-Based Outfit Recommendations

Rules consider:

Clothing categories (top, bottom, shoes, outerwear)

Weather temperature

Occasion

Basic color harmony

**How to Add Clothing Items**
Option A: Upload via Streamlit

Run the app

Upload a .jpg / .png

App auto-extracts:

Type (via simple classifier)

Dominant RGB color

Saves to DB + image folder

Option B: Use Colab + Post-Processor

Upload images to Google Colab folder

Run teammate A’s notebook → outputs tags_colab.csv

Save to data/tags_colab.csv

Run:

python -m src.utils.colab_postprocess
python scripts/sync_db.py

Configuration
Environment Setup
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Required Packages
streamlit
pillow
pandas
scikit-learn
python-dotenv
torch (if using the full Colab model locally)

Example Recommendation Output

Sample result from the Streamlit UI:

— Outfit —
[Top]    flannel (id=3)
[Bottom] jeans (id=7)
[Shoes]  running shoe (id=1)


Images appear side-by-side with color fallback if the image is missing.

Testing

To test the DB and pipeline:

python -m src.utils.data_loader
python -m src.db.db --init
python scripts/sync_db.py


To test recommendation logic:

python -m src.recommender.rules

**Known Limitations**

ImageNet labels can be noisy (e.g., calling a hoodie a “cardigan”).

Color extraction is approximate (KMeans on resized image).

Rule-based recommendation is simple; ML-based matching is a possible extension.

Currently does not detect patterns (plaid, striped, etc.) without enabling it.

**Future Work**

Add deep-learning clothing type classifier (custom trained)

Embedding-based outfit similarity (CLIP)

User preference learning

Closet analytics (“most worn color”, “unused items”, etc.)

Better season detection

Full mobile app version

**Team Members**

Jaylyn Lowes — Pipeline, Data Integration, Streamlit UI

Brianna Moore — Google Colab AI Model

Christopher McDonald — Recommender Engine

ShaKaylah Macklin— UI/UX + Image Rendering
