import shutil
import subprocess

from .base import PackageProvider


class WingetProvider(PackageProvider):
    @property
    def name(self) -> str:
        return "winget"

    def is_available(self) -> bool:
        return shutil.which("winget") is not None

    def update_indexes(self) -> bool:
        return self.is_available()

    def is_installed(self, package_name: str) -> bool:
        try:
            res = self._run_cmd(["winget", "list", "--id", package_name, "--exact"])
            return res.returncode == 0 and package_name.lower() in res.stdout.lower()
        except subprocess.CalledProcessError:
            return False

    def install(self, package_name: str) -> bool:
        try:
            self._run_cmd(
                [
                    "winget",
                    "install",
                    "--id",
                    package_name,
                    "--exact",
                    "--accept-package-agreements",
                    "--accept-source-agreements",
                ]
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def remove(self, package_name: str) -> bool:
        try:
            self._run_cmd(["winget", "uninstall", "--id", package_name, "--exact"])
            return True
        except subprocess.CalledProcessError:
            return False
