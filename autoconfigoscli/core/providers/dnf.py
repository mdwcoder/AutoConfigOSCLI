import shutil
import subprocess
from typing import List
from .base import PackageProvider

class DnfProvider(PackageProvider):
    @property
    def name(self) -> str:
        return "dnf"

    def is_available(self) -> bool:
        return shutil.which("dnf") is not None

    def update_indexes(self) -> bool:
        try:
            # dnf check-update returns 100 if updates are available, 0 if not, 1 on error
            # We want to refresh metadata mainly.
            # dnf makecache is better for refreshing metadata
            self._run_cmd(["dnf", "makecache"], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def is_installed(self, package_name: str) -> bool:
        try:
            res = self._run_cmd(["dnf", "list", "installed", package_name])
            return res.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def install(self, package_name: str) -> bool:
        try:
            self._run_cmd(["dnf", "install", "-y", package_name], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def remove(self, package_name: str) -> bool:
        try:
            self._run_cmd(["dnf", "remove", "-y", package_name], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False
