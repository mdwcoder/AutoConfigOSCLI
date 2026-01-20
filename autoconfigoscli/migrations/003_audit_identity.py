import sqlite3

def up(conn: sqlite3.Connection) -> None:
    # System Audit Log
    conn.execute("""
        CREATE TABLE IF NOT EXISTS system_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            os_system TEXT,
            os_release TEXT,
            distro_id TEXT,
            cpu_info TEXT,
            ram_total_gb REAL,
            disk_free_gb REAL,
            shell TEXT,
            detected_tools TEXT
        )
    """)

    # User Identity (Single Row enforced by logic usually, or PK fixed)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_identity (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            role TEXT,
            level TEXT,
            machine_type TEXT,
            preferences_json TEXT,
            notes TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
