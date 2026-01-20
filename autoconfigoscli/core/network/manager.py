from .base import NetworkBackend
from .linux import LinuxNetworkBackend
from .macos import MacOSNetworkBackend
from ..os_detect import get_os_info
from typing import Optional

class NetworkManager:
    def __init__(self):
        self.backend = self._detect_backend()

    def _detect_backend(self) -> Optional[NetworkBackend]:
        os_info = get_os_info()
        if os_info.is_macos:
            return MacOSNetworkBackend()
        elif os_info.is_linux:
            return LinuxNetworkBackend()
        return None
