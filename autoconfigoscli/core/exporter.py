import json
from pathlib import Path
from typing import Dict, Any
from .state import StateManager
import time

class Exporter:
    def __init__(self):
        self.state = StateManager()

    def export_data(self, output_path: str):
        self.state.init_db()
        data = {
            "metadata": {
                "timestamp": time.time(),
                "version": 1
            },
            "tables": {}
        }
        
        tables = ["installed_packages", "applied_profiles", "history", "settings"]
        for table in tables:
            rows = self.state.execute_query(f"SELECT * FROM {table}")
            data["tables"][table] = [dict(row) for row in rows]
            
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
