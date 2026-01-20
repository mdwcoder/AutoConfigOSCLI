import shutil
import subprocess
from typing import List
from .base import PackageProvider

class PacmanProvider(PackageProvider):
    @property
    def name(self) -> str:
        return "pacman"

    def is_available(self) -> bool:
        return shutil.which("pacman") is not None

    def update_indexes(self) -> bool:
        try:
            # -Sy refreshes database
            self._run_cmd(["pacman", "-Sy"], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def is_installed(self, package_name: str) -> bool:
        try:
            # -Qi checks if installed
            res = self._run_cmd(["pacman", "-Qi", package_name])
            return res.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def install(self, package_name: str) -> bool:
        try:
            # -S installs, --noconfirm avoids prompts
            self._run_cmd(["pacman", "-S", "--noconfirm", package_name], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def remove(self, package_name: str) -> bool:
        try:
            # -Rns removes package + unneeded deps + config
            self._run_cmd(["pacman", "-Rns", "--noconfirm", package_name], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False
