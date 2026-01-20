import os
import yaml
import shutil
import time
from typing import Dict, Any, List, Optional
from rich.console import Console
from .loader import ProfileLoader

console = Console()

class UserProfileManager:
    def __init__(self):
        self.loader = ProfileLoader()
        self.user_dir = self.loader.user_profiles_dir
        self.backup_dir = os.path.expanduser("~/.autoconfigoscli/backups/profiles")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def exists(self, name: str) -> bool:
        """Check if profile exists strictly in user dir or built-in."""
        # Check conflict with built-in
        builtin_path = os.path.join(self.loader.profiles_dir, f"{name}.yaml")
        if os.path.exists(builtin_path):
            return True # It "exists" generally, but we can't overwrite built-in as user profile name easily without warning
            
        user_path = os.path.join(self.user_dir, f"{name}.yaml")
        return os.path.exists(user_path)

    def is_user_profile(self, name: str) -> bool:
        return os.path.exists(os.path.join(self.user_dir, f"{name}.yaml"))

    def is_builtin(self, name: str) -> bool:
        return os.path.exists(os.path.join(self.loader.profiles_dir, f"{name}.yaml"))

    def create(self, name: str, data: Dict[str, Any], overwrite: bool = False) -> bool:
        path = os.path.join(self.user_dir, f"{name}.yaml")
        
        if self.is_builtin(name):
            console.print(f"[red]Error: '{name}' conflicts with a built-in profile by that name.[/red]")
            return False
            
        if os.path.exists(path) and not overwrite:
             console.print(f"[yellow]Profile '{name}' already exists. Use overwrite=True.[/yellow]")
             return False

        if os.path.exists(path):
            self._backup_profile(name)

        try:
            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            console.print(f"[red]Failed to create profile: {e}[/red]")
            return False

    def delete(self, name: str) -> bool:
        path = os.path.join(self.user_dir, f"{name}.yaml")
        if not os.path.exists(path):
            console.print(f"[red]User profile '{name}' not found.[/red]")
            return False
            
        self._backup_profile(name)
        try:
            os.remove(path)
            return True
        except Exception as e:
            console.print(f"[red]Failed to delete profile: {e}[/red]")
            return False
            
    def load_raw(self, name: str) -> Optional[Dict[str, Any]]:
        path = os.path.join(self.user_dir, f"{name}.yaml")
        if not os.path.exists(path):
             return None
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except:
             return None

    def _backup_profile(self, name: str):
        path = os.path.join(self.user_dir, f"{name}.yaml")
        if not os.path.exists(path):
            return
            
        ts = int(time.time())
        backup_name = f"{name}_{ts}.yaml"
        backup_path = os.path.join(self.backup_dir, backup_name)
        try:
            shutil.copy2(path, backup_path)
            console.print(f"[dim]Backed up {name} to {backup_name}[/dim]")
        except Exception as e:
            console.print(f"[red]Backup failed: {e}[/red]")
