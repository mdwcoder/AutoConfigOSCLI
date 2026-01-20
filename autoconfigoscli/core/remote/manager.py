from typing import Dict, Any, Optional
import os
import json
from .ssh import SSHWrapper
from .bootstrap import BootstrapManager

class RemoteManager:
    def __init__(self, port: int = 22, key_path: Optional[str] = None):
        self.ssh = SSHWrapper(port, key_path)
        self.bootstrap = BootstrapManager(self.ssh)

    def _prepare_target(self, target: str) -> Optional[str]:
        """Ensures target has deps and tool deployed. Returns remote_path or None."""
        ok, missing = self.bootstrap.check_dependencies(target)
        if not ok:
            # Try install? Or fail?
            # For now, simplistic:
            if not self.bootstrap.install_dependencies(target, missing):
                return None
        
        success, remote_path = self.bootstrap.deploy_tool(target)
        if not success:
            return None
        return remote_path

    def install_profile(self, target: str, profile_name: str, local_profile_path: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """
        Orchestrates remote install.
        1. Bootstrap
        2. Copy profile if local
        3. Run remote install
        4. Cleanup
        """
        path = self._prepare_target(target)
        if not path:
             return {"success": False, "error": "Bootstrap failed"}
             
        try:
            # If local profile provided, copy it
            if local_profile_path:
                 # Ensure remote profiles dir exists
                 self.ssh.run_command(target, f"mkdir -p {path}/profiles/user")
                 remote_prof_path = f"{path}/profiles/user/{os.path.basename(local_profile_path)}"
                 if not self.ssh.copy_file(target, local_profile_path, remote_prof_path):
                     return {"success": False, "error": "Profile transfer failed"}
                     
            # Run install command
            flags = "--dry-run" if dry_run else "--yes"
            cmd = f"source venv/bin/activate && python3 -m autoconfigoscli.cli install {profile_name} {flags}"
            
            # Exec relative to repo root
            full_cmd = f"cd {path} && {cmd}"
            
            # Stream output?
            # For API return, we capture. 
            success, out, err = self.ssh.run_command(target, full_cmd)
            
            return {
                "success": success,
                "stdout": out,
                "stderr": err
            }
        finally:
            self.bootstrap.cleanup(target, path)

    def run_generic(self, target: str, command: str, args: str = "") -> Dict[str, Any]:
        """Run status, audit, doctor."""
        path = self._prepare_target(target)
        if not path:
             return {"success": False, "error": "Bootstrap failed"}
             
        try:
            full_cmd = f"cd {path} && source venv/bin/activate && python3 -m autoconfigoscli.cli {command} {args}"
            success, out, err = self.ssh.run_command(target, full_cmd)
            return {"success": success, "stdout": out, "stderr": err}
        finally:
            self.bootstrap.cleanup(target, path)
