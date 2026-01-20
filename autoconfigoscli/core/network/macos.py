from typing import List, Dict, Any
import subprocess
from .base import NetworkBackend

class MacOSNetworkBackend(NetworkBackend):
    @property
    def name(self) -> str:
        return "macos-networksetup"

    def is_available(self) -> bool:
        # Check if running on mac
        import platform
        return platform.system() == "Darwin"

    def get_status(self) -> List[Dict[str, Any]]:
        # networksetup -listallhardwareports provided map
        return []

    def set_dhcp(self, interface: str) -> bool:
        return False

    def set_static(self, interface: str, ip: str, mask: str, gateway: str) -> bool:
        return False

    def set_dns(self, interface: str, servers: List[str]) -> bool:
        return False

    def backup_config(self, interface: str) -> str:
        return ""

    def restore_config(self, backup_data: str) -> bool:
        return False
