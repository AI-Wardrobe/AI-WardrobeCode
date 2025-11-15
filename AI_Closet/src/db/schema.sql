
-- SQLite schema for wardrobe
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    type TEXT,
    dominant_color TEXT,
    pattern TEXT,
    season TEXT,
    formality INTEGER,
    notes TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_ids TEXT NOT NULL, -- comma-separated ids for outfit
    label TEXT CHECK(label IN ('like','dislike')) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
