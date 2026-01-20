import shutil
import subprocess
from typing import List
from .base import PackageProvider

class BrewProvider(PackageProvider):
    @property
    def name(self) -> str:
        return "brew"

    def is_available(self) -> bool:
        return shutil.which("brew") is not None

    def update_indexes(self) -> bool:
        try:
            self._run_cmd(["brew", "update"])
            return True
        except subprocess.CalledProcessError:
            return False

    def is_installed(self, package_name: str) -> bool:
        try:
            # brew list --formula shows installed formulae
            # Check if package is in the output of brew list
            res = self._run_cmd(["brew", "list", "--formula", package_name])
            return res.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def install(self, package_name: str) -> bool:
        try:
            self._run_cmd(["brew", "install", package_name])
            return True
        except subprocess.CalledProcessError:
            return False

    def remove(self, package_name: str) -> bool:
        try:
            self._run_cmd(["brew", "uninstall", package_name])
            return True
        except subprocess.CalledProcessError:
            return False
