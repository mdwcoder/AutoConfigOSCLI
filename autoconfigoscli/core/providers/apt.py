import shutil
import subprocess
from typing import List
from .base import PackageProvider

class AptProvider(PackageProvider):
    @property
    def name(self) -> str:
        return "apt"

    def is_available(self) -> bool:
        return shutil.which("apt-get") is not None

    def update_indexes(self) -> bool:
        try:
            self._run_cmd(["apt-get", "update"], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def is_installed(self, package_name: str) -> bool:
        try:
            # dpkg -s returns 0 if installed
            res = self._run_cmd(["dpkg", "-s", package_name])
            return res.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def install(self, package_name: str) -> bool:
        try:
            # -y for non-interactive
            self._run_cmd(["apt-get", "install", "-y", package_name], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def remove(self, package_name: str) -> bool:
        try:
            self._run_cmd(["apt-get", "remove", "-y", package_name], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False
