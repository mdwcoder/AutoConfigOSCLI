from typing import List, Dict, Any
import subprocess
import shutil
from .base import NetworkBackend

class LinuxNetworkBackend(NetworkBackend):
    def __init__(self):
        self._tool = self._detect_tool()

    def _detect_tool(self):
        if shutil.which("nmcli"): return "nmcli"
        # Others not implemented yet
        return None

    @property
    def name(self) -> str:
        return f"linux-{self._tool}"

    def is_available(self) -> bool:
        return self._tool is not None

    def get_status(self) -> List[Dict[str, Any]]:
        if self._tool == "nmcli":
             # nmcli -t -f DEVICE,STATE,CONNECTION device
             try:
                 res = subprocess.run(["nmcli", "-t", "-f", "DEVICE,STATE,CONNECTION", "device"], capture_output=True, text=True)
                 lines = res.stdout.strip().split('\n')
                 status = []
                 for line in lines:
                     parts = line.split(':')
                     if len(parts) >= 2:
                         status.append({"interface": parts[0], "state": parts[1], "connection": parts[2] if len(parts) > 2 else ""})
                 return status
             except:
                 pass
        return []

    def set_dhcp(self, interface: str) -> bool:
        if self._tool == "nmcli":
            try:
                subprocess.run(["nmcli", "con", "mod", interface, "ipv4.method", "auto"], check=True)
                subprocess.run(["nmcli", "con", "up", interface], check=True)
                return True
            except:
                return False
        return False

    def set_static(self, interface: str, ip: str, mask: str, gateway: str) -> bool:
        return False # TODO

    def set_dns(self, interface: str, servers: List[str]) -> bool:
        return False # TODO
        
    def backup_config(self, interface: str) -> str:
        # Simplistic backup for nmcli: export connection profile
        if self._tool == "nmcli":
             try:
                 res = subprocess.run(["nmcli", "con", "show", interface], capture_output=True, text=True)
                 return res.stdout
             except:
                 return ""
        return ""

    def restore_config(self, backup_data: str) -> bool:
        return False # Hard with plain text dump
