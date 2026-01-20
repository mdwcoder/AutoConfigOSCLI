import json
from typing import Dict, Any, Optional
from rich.prompt import Prompt, Confirm
from .state import StateManager

class IdentityManager:
    def __init__(self):
        self.state = StateManager()

    def get_identity(self) -> Dict[str, Any]:
        """Returns the current user identity or default structure."""
        self.state.init_db() # ensure db
        try:
            rows = self.state.execute_query("SELECT * FROM user_identity WHERE id = 1")
            if rows:
                row = rows[0]
                return {
                    "role": row['role'],
                    "level": row['level'],
                    "machine_type": row['machine_type'],
                    "preferences": json.loads(row['preferences_json'] or "{}"),
                    "notes": row['notes'],
                    "updated_at": row['updated_at']
                }
        except Exception:
            pass
            
        return {
            "role": "Not Set",
            "level": "Unspecified",
            "machine_type": "Laptop",
            "preferences": {},
            "notes": ""
        }

    def update_identity(self, data: Dict[str, Any]) -> bool:
        """Updates the user identity row."""
        self.state.init_db()
        try:
            self.state.execute_query("""
                INSERT INTO user_identity (id, role, level, machine_type, preferences_json, notes, updated_at)
                VALUES (1, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    role=excluded.role,
                    level=excluded.level,
                    machine_type=excluded.machine_type,
                    preferences_json=excluded.preferences_json,
                    notes=excluded.notes,
                    updated_at=CURRENT_TIMESTAMP
            """, (
                data.get("role"),
                data.get("level"),
                data.get("machine_type"),
                json.dumps(data.get("preferences", {})),
                data.get("notes")
            ))
            return True
        except Exception as e:
            return False

    def interactive_edit(self):
        """Runs a CLI wizard to edit identity."""
        current = self.get_identity()
        
        print("\n--- User Identity Configuration ---\n")
        
        new_role = Prompt.ask("Primary Role", default=current["role"], choices=["backend", "frontend", "devops", "student", "fullstack", "ai-engineer", "data-scientist"])
        new_level = Prompt.ask("Experience Level", default=current["level"], choices=["junior", "mid", "senior", "lead", "architect"])
        new_machine = Prompt.ask("Machine Type", default=current["machine_type"], choices=["laptop", "desktop", "server"])
        
        # Preferences
        prefs = current.get("preferences", {})
        prefs["tier_preference"] = Prompt.ask("Preferred Profile Tier", default=prefs.get("tier_preference", "mid"), choices=["lite", "mid", "full"])
        
        notes = Prompt.ask("Additional Notes", default=current["notes"])

        if Confirm.ask("Save Identity?"):
            success = self.update_identity({
                "role": new_role,
                "level": new_level,
                "machine_type": new_machine,
                "preferences": prefs,
                "notes": notes
            })
            if success:
                print("Identity saved successfully.")
            else:
                print("Failed to save identity.")
