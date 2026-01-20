import os
import re
from typing import Dict, Any, Optional, List
from .base import AIProvider
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from ..core.state import StateManager

class AIManager:
    def __init__(self):
        self.state = StateManager()
        self.provider: Optional[AIProvider] = None
        self._load_provider()

    def _load_provider(self):
        # Check config preference
        # We might need a settings table or simple file. 
        # For now, priority: Config > Env Var > Default (Gemini)
        
        # Check if user set a preference
        pref_provider = self._get_preference("ai_provider")
        
        if pref_provider == "openai":
            self.provider = OpenAIProvider()
        elif pref_provider == "gemini":
            self.provider = GeminiProvider()
        else:
            # Auto-detect based on keys
            if os.environ.get("GEMINI_API_KEY"):
                self.provider = GeminiProvider()
            elif os.environ.get("OPENAI_API_KEY"):
                self.provider = OpenAIProvider()
            else:
                self.provider = None

    def _get_preference(self, key: str) -> Optional[str]:
        # Simple query to settings table if it exists, or just return None
        try:
            self.state.init_db()
            cur = self.state.conn.execute("SELECT value FROM settings WHERE key=?", (key,))
            row = cur.fetchone()
            return row[0] if row else None
        except:
             return None

    def set_provider(self, name: str) -> bool:
        if name not in ["gemini", "openai", "none"]:
            return False
            
        try:
            self.state.execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("ai_provider", name))
            self._load_provider() # Reload
            return True
        except:
            return False
            
    def get_active_provider_name(self) -> str:
        if isinstance(self.provider, GeminiProvider): return "gemini"
        if isinstance(self.provider, OpenAIProvider): return "openai"
        return "none"

    def scrub_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Removes PII from context before sending to AI."""
        # Deep copy to avoid mutating original
        import copy
        safe_ctx = copy.deepcopy(context)
        
        # 1. Scrub Usernames from paths
        # Helper to scrub recursively?
        
        def scrub_str(s: str) -> str:
            # Replace home dir
            home = os.path.expanduser("~")
            if home in s and home != "/":
                s = s.replace(home, "$HOME")
            return s
            
        # Recursive scrub
        def recursive_scrub(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    obj[k] = recursive_scrub(v)
            elif isinstance(obj, list):
                for i in range(len(obj)):
                    obj[i] = recursive_scrub(obj[i])
            elif isinstance(obj, str):
                return scrub_str(obj)
            return obj
            
        safe_ctx = recursive_scrub(safe_ctx)
        
        # 2. Specific field scrubbing
        if 'identity' in safe_ctx:
            # Remove raw names if present? 
            # Our identity object currently has role, level, preferences, notes.
            # Notes might be sensitive.
            if 'notes' in safe_ctx['identity']:
                 safe_ctx['identity']['notes'] = "[REDACTED]"
                 
        return safe_ctx

    def recommend(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.provider or not self.provider.is_available:
            return {"error": "No AI provider configured or available."}
            
        safe_context = self.scrub_context(context)
        return self.provider.recommend(safe_context)

    def explain(self, context: Dict[str, Any], query: str) -> str:
        if not self.provider or not self.provider.is_available:
            return "No AI provider configured or available."
            
        safe_context = self.scrub_context(context)
        return self.provider.explain(safe_context, query)
