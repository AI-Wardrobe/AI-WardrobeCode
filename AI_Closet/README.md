
# AI Closet (Web/Jupyter Prototype)

A decision-support system that recommends outfits from a digital wardrobe using computer vision, rules, and (optionally) learning-based re‑ranking.

## Quickstart
1) Create a Python 3.10+ environment and activate it.
2) `pip install -r requirements.txt`
3) Copy `.env.example` to `.env` and edit values if needed.
4) Initialize the database: `python -m src.db.db --init`
5) (Option A) Run the Streamlit app: `streamlit run src/interface/streamlit_app.py`
6) (Option B) Open `notebooks/00_demo.ipynb` in Jupyter and run cells.

## Structure
```
AI_Closet/
├── data/                 # user images + generated metadata
├── notebooks/            # Jupyter experiments & demos
├── src/
│   ├── vision/           # CV tagger
│   ├── recommender/      # rules + learning
│   ├── db/               # SQLite helpers
│   └── interface/        # Streamlit/Jupyter UI
└── tests/                # unit tests (rules, db, cv)
```

## Licensing
This starter is provided for educational use.
