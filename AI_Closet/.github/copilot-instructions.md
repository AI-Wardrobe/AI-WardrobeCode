<!-- Copilot / AI agent guidance for the AI_Closet project -->
# AI_Closet — Copilot Instructions

This file gives concise, actionable pointers so an AI coding agent can be productive in this repository immediately.

## Big Picture
- **Purpose:** a lightweight decision-support prototype that recommends outfits from a digital wardrobe using simple CV tagging + rule-based recommender. Primary usage is via the Streamlit UI (`src/interface/streamlit_app.py`) or the Jupyter demo (`notebooks/00_demo.ipynb`).
- **Major components:**
  - `src/vision/` — computer vision helpers (tagging, color extraction).
  - `src/recommender/` — rule-based recommendation logic (`rules.py`); uses an `Item` dataclass and returns outfit lists.
  - `src/db/` — thin SQLite helpers (`db.py`) exposing `init_db`, `add_item`, `list_items`.
  - `src/interface/` — Streamlit app and Jupyter helper; Streamlit is the primary dev UI.
  - `src/utils/` — data ingestion utilities (e.g., `data_loader.py` for loading tag CSVs and syncing to DB).

## Important developer workflows (run these locally)
- Create and activate Python 3.10+ environment and install deps: `pip install -r requirements.txt` (see `README.md`).
- Initialize DB schema: `python -m src.db.db --init` (this creates `wardrobe.db` used by the app).
- Run the web UI: `streamlit run src/interface/streamlit_app.py` — this is the quickest way to exercise full upload → tag → recommend flow.
- Run unit tests: use the bundled unittest files, e.g. `python -m unittest discover -v` (tests live in `tests/`).

## Project-specific patterns and conventions
- Color strings: CV and UI use `rgb(r,g,b)` strings (see `src/vision/tagger.py` and `src/recommender/rules.py`). Treat these as simple strings in rules unless you call color helpers.
- Flexible CSV ingestion: `src/utils/data_loader.py::load_tags_csv` accepts multiple column names — expect `filename|image_name`, `type|predicted_type`, `dominant_color|color`. When adding fields, follow this tolerant lookup style.
- DB helpers: prefer `src/db/db.py` functions (`add_item`, `list_items`, `init_db`) rather than direct SQL in other modules. Use `init_db()` before inserts in CLI flows.
- Recommender API: `recommend(items: List[Item], context: Dict) -> List[List[Item]]`. `Item` is a dataclass in `src/recommender/rules.py`. Keep new recommender code compatible with that simple interface for Streamlit and tests.

## Integration points & examples
- Streamlit upload flow (example): `src/interface/streamlit_app.py` saves files to `data/images/`, extracts dominant color via `src.vision.tagger.extract_dominant_color`, maps filename→type with `classify_type_from_name`, then calls `add_item(...)`.
- CSV sync example: `src/utils/data_loader.py::load_and_sync()` calls `add_item(...)` for each row; it normalizes column names to lowercase and skips rows without a valid filename.
- Tests: `tests/test_rules.py` constructs `Item(...)` objects and calls `recommend(...)` directly — follow that pattern for small, fast unit tests.

## Things the agent should avoid / be cautious about
- Do not assume a separate config file — environment hints are in `README.md` (`.env.example` may be referenced but not present). If you add runtime config, document it.
- Files are referenced by relative paths computed from module locations (see `BASE_DIR` in `src/utils/data_loader.py`). Use the existing helpers to compute data paths rather than hardcoding absolute paths.

## Quick references (files to inspect)
- Streamlit UI: `src/interface/streamlit_app.py` (upload → save → tag → DB → recommend)
- Recommender rules: `src/recommender/rules.py` (Item dataclass; `recommend()` signature)
- Data ingestion: `src/utils/data_loader.py` (CSV normalization and DB sync)
- DB layer: `src/db/db.py` (init, add, list helpers)
- Tests: `tests/test_rules.py` (example unit test)

## Helpful concrete tasks for an agent
- Small bugfix: ensure `load_tags_csv()` robustly handles missing columns (follow current tolerant style).
- Add a unit test for edge-case row where `formality` is non-numeric (see `sync_items_from_df`).
- Improve `recommend()` scoring by adding a deterministic sort — keep function signature stable for Streamlit.

If anything here is unclear or you'd like more examples (e.g., sample DB schema or CV helper details), tell me which area to expand and I'll update this file.
