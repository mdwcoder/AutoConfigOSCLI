from abc import ABC, abstractmethod
from typing import List, Optional
import subprocess
import shutil

class PackageProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the package manager (e.g., 'brew', 'apt')."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if the package manager is installed on the system."""
        pass

    @abstractmethod
    def update_indexes(self) -> bool:
        """Updates the package indexes (e.g., apt update)."""
        pass

    @abstractmethod
    def is_installed(self, package_name: str) -> bool:
        """Checks if a specific package is installed."""
        pass

    @abstractmethod
    def install(self, package_name: str) -> bool:
        """Installs a package."""
        pass

    @abstractmethod
    def remove(self, package_name: str) -> bool:
        """Removes a package."""
        pass

    def _run_cmd(self, cmd: List[str], sudo: bool = False) -> subprocess.CompletedProcess:
        """Helper to run commands safely."""
        if sudo:
            # Check if we are already root to avoid redundant sudo
            # but for now, rely on user being sudoer
            cmd = ["sudo"] + cmd
        
        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            # Log error separately if needed
            raise e
