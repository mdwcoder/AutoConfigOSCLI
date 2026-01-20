from typing import Dict, List, Any, Optional
import yaml
import os
from pathlib import Path

class Profile:
    def __init__(self, name: str, data: Dict[str, Any]):
        self.name = name
        self.description = data.get("description", "")
        self.tier = data.get("tier", "mid") # lite, mid, full
        self.tags = data.get("tags", [])
        self.env_vars = data.get("env", {})
        self.scripts = data.get("scripts", {})
        
        # New Schema: packages is a list of IDs
        self.packages: List[str] = data.get("packages", [])

class ProfileLoader:
    def __init__(self, profiles_dir: str = None):
        if profiles_dir:
            self.profiles_dir = profiles_dir
        else:
            self.profiles_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                "profiles"
            )

    def list_profiles(self) -> List[str]:
        if not os.path.exists(self.profiles_dir):
            return []
        return [f.replace(".yaml", "") for f in os.listdir(self.profiles_dir) if f.endswith(".yaml")]

    def load_profile(self, name: str) -> Optional[Profile]:
        path = os.path.join(self.profiles_dir, f"{name}.yaml")
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                return Profile(name, data)
        except Exception:
            return None
