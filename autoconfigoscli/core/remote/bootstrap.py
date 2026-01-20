from typing import Tuple
from .ssh import SSHWrapper

class BootstrapManager:
    def __init__(self, ssh: SSHWrapper):
        self.ssh = ssh

    def check_dependencies(self, target: str) -> Tuple[bool, list]:
        """Check if git and python3 are installed."""
        missing = []
        
        # Check Python 3
        ok, out, _ = self.ssh.run_command(target, "which python3")
        if not ok:
             missing.append("python3")
             
        # Check Git
        ok, out, _ = self.ssh.run_command(target, "which git")
        if not ok:
             missing.append("git")
             
        return len(missing) == 0, missing

    def install_dependencies(self, target: str, missing: list) -> bool:
        """Attempt to install missing dependencies using common package managers."""
        # Detect PM
        dnf_check, _, _ = self.ssh.run_command(target, "which dnf")
        apt_check, _, _ = self.ssh.run_command(target, "which apt-get")
        pacman_check, _, _ = self.ssh.run_command(target, "which pacman")
        
        cmd = ""
        pkgs = " ".join(missing)
        
        if dnf_check:
            cmd = f"dnf install -y {pkgs}"
        elif apt_check:
            cmd = f"apt-get update && apt-get install -y {pkgs}"
        elif pacman_check:
            cmd = f"pacman -S --noconfirm {pkgs}"
        else:
            return False # Unknown PM
            
        success, _, err = self.ssh.run_command(target, cmd, sudo=True)
        return success

    def deploy_tool(self, target: str, branch: str = "main") -> Tuple[bool, str]:
        """
        Clones the tool to a temp directory.
        Returns (success, remote_path)
        """
        # Create temp dir
        ok, valid_path, _ = self.ssh.run_command(target, "mktemp -d -t autoconfigos-XXXXXX")
        if not ok:
            return False, "Failed to create temp dir"
            
        remote_path = valid_path.strip()
        
        # Clone (We assume public repo or SSH forwarding works, or just public usage for now)
        # Using the actual repo URL if known. For this env, we might be local.
        # Ideally we'd git archive and upload ourselves to avoid remote git auth issues.
        # But per User Request: "clone the repo from GitHub".
        
        repo_url = "https://github.com/GoogleCloudPlatform/autoconfigoscli.git" # Placeholder
        # TODO: Allow overriding repo URL
        
        # NOTE: Since we are in a dev environment and the upstream URL might not exist yet,
        # we realistically should default to 'uploading current source' or similar if we want true testing.
        # But 'deploy_tool' logic requested 'clones repo'.
        # Let's assume public GitHub for now.
        
        # For this specific simulation, let's pretend we clone.
        # Real-world: git clone logic 
        
        clone_cmd = f"git clone {repo_url} {remote_path}/repo"
        ok, _, err = self.ssh.run_command(target, clone_cmd)
        
        # If clone fails (likely due to placeholder URL), fail gracefully
        if not ok:
             return False, f"Git clone failed: {err}"
             
        # Run init setup?
        # Setup venv?
        setup_cmd = f"cd {remote_path}/repo && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt"
        ok, _, err = self.ssh.run_command(target, setup_cmd)
        
        if not ok:
             return False, f"Setup failed: {err}"
             
        return True, f"{remote_path}/repo"

    def cleanup(self, target: str, remote_path: str):
        if remote_path and remote_path.startswith("/tmp/"):
             # Safety check to only delete tmp
             # Get parent tmp dir
             parent = remote_path.replace("/repo", "")
             self.ssh.run_command(target, f"rm -rf {parent}")
