import sqlite3
import json
from typing import Dict, Any, Optional
from ..state import StateManager
from ..audit import SystemAuditor

class MachineManager:
    def __init__(self):
        self.state = StateManager()
        self.auditor = SystemAuditor()

    def get_profile(self) -> Dict[str, Any]:
        """Returns current machine profile. If not set, guesses defaults."""
        self.state.init_db()
        try:
            rows = self.state.execute_query("SELECT * FROM machine_profile WHERE id = 1")
            if rows:
                row = rows[0]
                return {
                    "type": row['type'],
                    "usage": row['usage'],
                    "power": row['power'],
                    "gui": bool(row['gui']),
                    "notes": row['notes'],
                    "updated_at": row['updated_at']
                }
        except Exception:
            pass
            
        # Fallback: Deduce from Audit
        return self._guess_defaults()

    def _guess_defaults(self) -> Dict[str, Any]:
        """Analyzes system audit to guess machine type and power."""
        audit_data = self.auditor.run_audit()
        
        # Power Guess
        # Logic: High if > 8 cores or > 16GB RAM
        # Mid if > 4 cores or > 8GB RAM
        # Low otherwise
        cpu_cores = 4 # buffer default
        if "cores" in audit_data["cpu_info"]:
            try:
                # e.g. "x86_64 (12 cores)" -> extract 12
                # simplistic parse
                parts = audit_data["cpu_info"].split("(")
                if len(parts) > 1:
                    cpu_cores = int(parts[1].split()[0])
            except: pass
        
        ram = audit_data["ram_total_gb"]
        
        power = "mid"
        if cpu_cores >= 8 or ram >= 16:
            power = "high"
        elif cpu_cores < 4 and ram < 8:
            power = "low"
            
        # Type Guess (Hard to be precise, assume laptop/desktop based on battery? or just 'desktop' default)
        # For now default to 'laptop' as safe bet for dev tools, or 'desktop'
        m_type = "laptop" 
        
        # GUI Guess
        # Check TERM or DESKTOP_SESSION env var
        import os
        gui = True
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
             if "ssh" in os.environ.get("SSH_CONNECTION", "").lower():
                 gui = False
        
        return {
            "type": m_type,
            "usage": "personal", # Safe default
            "power": power,
            "gui": gui,
            "notes": "Auto-detected defaults",
            "updated_at": None # Not saved yet
        }

    def update_profile(self, data: Dict[str, Any]) -> bool:
        self.state.init_db()
        try:
            self.state.execute_query("""
                INSERT INTO machine_profile (id, type, usage, power, gui, notes, updated_at)
                VALUES (1, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    type=excluded.type,
                    usage=excluded.usage,
                    power=excluded.power,
                    gui=excluded.gui,
                    notes=excluded.notes,
                    updated_at=CURRENT_TIMESTAMP
            """, (
                data.get("type"),
                data.get("usage"),
                data.get("power"),
                1 if data.get("gui") else 0,
                data.get("notes")
            ))
            return True
        except Exception:
            return False

    def reset_profile(self) -> bool:
        """Resets to detected defaults (by deleting the row so get_profile guesses again, or explicitly overwriting?) 
           Explicitly overwriting is better to persist the reset state."""
        defaults = self._guess_defaults()
        return self.update_profile(defaults)
