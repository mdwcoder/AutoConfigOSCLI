import subprocess
import logging
import shlex
from typing import Optional, Tuple

class SSHWrapper:
    def __init__(self, port: int = 22, key_path: Optional[str] = None):
        self.port = port
        self.key_path = key_path

    def _build_base_cmd(self, target: str) -> list:
        cmd = ["ssh", "-p", str(self.port)]
        if self.key_path:
            cmd.extend(["-i", self.key_path])
        
        # StrictHostKeyChecking=no helps for automation validation, but risky for prod.
        # User specified "secure", so let's keep default checks but maybe 
        # BatchMode=yes to fail fast on auth issues.
        cmd.extend(["-o", "BatchMode=yes"])
        cmd.extend(["-o", "ConnectTimeout=10"])
        cmd.append(target)
        return cmd

    def run_command(self, target: str, command: str, sudo: bool = False, stream_output: bool = False) -> Tuple[bool, str, str]:
        """
        Runs a command on the remote target.
        Returns: (success, stdout, stderr)
        """
        if sudo:
            # We assume user has NOPASSWD sudo or we can't easily handle interactive password prompt via subprocess non-interactively
            # Alternatively, we could force pseudo-tty (-t) but that complicates capturing output.
            # Best practice for automation: assume key-based auth + sudo access.
            command = f"sudo -n {command}"

        base = self._build_base_cmd(target)
        base.append(command)

        logging.debug(f"SSH Exec: {' '.join(base)}")

        if stream_output:
            # For long running commands, we might want to stream to console.
            # But for return API, we probably just want result. 
            # If stream_output is True, we print directly and return empty strings?
            # Or we capture AND print?
            # Let's keep it simple: if stream, use Popen to pipe to existing stdout, return success bool only.
            
            try:
                subprocess.run(base, check=True)
                return True, "", ""
            except subprocess.CalledProcessError:
                return False, "", "Command failed (streamed)"
                
        else:
            try:
                result = subprocess.run(
                    base, 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
            except Exception as e:
                return False, "", str(e)

    def copy_file(self, target: str, local_path: str, remote_path: str) -> bool:
        """SCP a file to remote."""
        cmd = ["scp", "-P", str(self.port)]
        if self.key_path:
            cmd.extend(["-i", self.key_path])
        
        cmd.extend([local_path, f"{target}:{remote_path}"])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"SCP failed: {e.stderr}")
            return False
