import sqlite3

def up(conn: sqlite3.Connection) -> None:
    # Machine Profile (Single Row)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS machine_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            type TEXT,          -- laptop, desktop, server
            usage TEXT,         -- work, personal, lab
            power TEXT,         -- low, mid, high
            gui INTEGER,        -- 1 (true) or 0 (false)
            notes TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Decision History (Rich Action Log)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decision_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            action_type TEXT,   -- install_profile, install_package, etc.
            actor TEXT,         -- user, system
            source TEXT,        -- built-in, user-profile, manual
            target TEXT,        -- profile name or package id
            result TEXT,        -- success, skipped, failed
            details_json TEXT,  -- JSON with more info
            risks_json TEXT     -- JSON with acknowledged risks
        )
    """)
