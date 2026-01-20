from abc import ABC, abstractmethod
from typing import Dict, Any, List

class NetworkBackend(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the backend (e.g. NetworkManager, networksetup)."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_status(self) -> List[Dict[str, Any]]:
        """Returns list of interfaces and their status."""
        pass

    @abstractmethod
    def set_dhcp(self, interface: str) -> bool:
        pass

    @abstractmethod
    def set_static(self, interface: str, ip: str, mask: str, gateway: str) -> bool:
        pass

    @abstractmethod
    def set_dns(self, interface: str, servers: List[str]) -> bool:
        pass
        
    @abstractmethod
    def backup_config(self, interface: str) -> str:
        """Backs up configuration for specific interface and returns content/path."""
        pass
    
    @abstractmethod
    def restore_config(self, backup_data: str) -> bool:
        pass
