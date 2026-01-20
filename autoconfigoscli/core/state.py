import sqlite3
import os
from .migration_manager import MigrationManager

DB_PATH = os.path.expanduser("~/.autoconfigoscli/state.db")

class StateManager:
    def __init__(self, db_path: str = None):
        if db_path:
            self.db_path = db_path
        else:
            base_dir = os.path.expanduser("~/.autoconfigoscli")
            os.makedirs(base_dir, exist_ok=True)
            self.db_path = os.path.join(base_dir, "state.db")
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        # Run migrations
        with self.get_connection() as conn:
            manager = MigrationManager(conn)
            manager.run_migrations()

    def execute_query(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()
