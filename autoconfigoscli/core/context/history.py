import json
from typing import List, Dict, Any, Optional
from ..state import StateManager

class HistoryManager:
    def __init__(self):
        self.state = StateManager()

    def record_action(self, 
                      action_type: str, 
                      actor: str, 
                      source: str, 
                      target: str, 
                      result: str, 
                      details: Dict[str, Any] = None, 
                      risks: List[str] = None):
        """Records a decision/action in the rich history log."""
        self.state.init_db()
        try:
            self.state.execute_query("""
                INSERT INTO decision_history (
                    action_type, actor, source, target, result, details_json, risks_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                action_type, actor, source, target, result,
                json.dumps(details or {}),
                json.dumps(risks or [])
            ))
        except Exception:
            pass

    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        self.state.init_db()
        try:
            rows = self.state.execute_query(
                f"SELECT * FROM decision_history ORDER BY id DESC LIMIT {limit}"
            )
            return [dict(row) for row in rows]
        except Exception:
            return []

    def get_details(self, entry_id: int) -> Optional[Dict[str, Any]]:
        self.state.init_db()
        try:
            rows = self.state.execute_query(
                "SELECT * FROM decision_history WHERE id = ?", (entry_id,)
            )
            if rows:
                row = dict(rows[0])
                # Parse JSON fields
                if row['details_json']:
                    row['details'] = json.loads(row['details_json'])
                if row['risks_json']:
                    row['risks'] = json.loads(row['risks_json'])
                return row
        except Exception:
            pass
        return None
