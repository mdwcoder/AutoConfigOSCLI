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
        
        self.user_profiles_dir = os.path.expanduser("~/.autoconfigoscli/profiles/user")
        if not os.path.exists(self.user_profiles_dir):
            try:
                os.makedirs(self.user_profiles_dir)
            except OSError:
                pass

    def list_profiles(self) -> List[str]:
        profiles = set()
        
        # Built-in
        if os.path.exists(self.profiles_dir):
            for f in os.listdir(self.profiles_dir):
                if f.endswith(".yaml"):
                    profiles.add(f.replace(".yaml", ""))
        
        # User
        if os.path.exists(self.user_profiles_dir):
            for f in os.listdir(self.user_profiles_dir):
                if f.endswith(".yaml"):
                    profiles.add(f.replace(".yaml", ""))
                    
        return sorted(list(profiles))

    def load_profile(self, name: str) -> Optional[Profile]:
        # Check User Profile first
        user_path = os.path.join(self.user_profiles_dir, f"{name}.yaml")
        if os.path.exists(user_path):
            path = user_path
            source = "user"
        else:
            path = os.path.join(self.profiles_dir, f"{name}.yaml")
            source = "built-in"
            
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                p = Profile(name, data)
                # We could add source metadata here if Profile class supported it
                return p
        except Exception:
            return None
