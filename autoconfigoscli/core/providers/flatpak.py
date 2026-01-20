import shutil
import subprocess
from typing import List, Optional
from rich.console import Console
from rich.prompt import Confirm
from .base import PackageProvider

console = Console()

class FlatpakProvider(PackageProvider):
    def __init__(self, system_provider: Optional[PackageProvider] = None):
        self.system_provider = system_provider

    @property
    def name(self) -> str:
        return "flatpak"

    def is_available(self) -> bool:
        return shutil.which("flatpak") is not None

    def bootstrap(self) -> bool:
        """Installs flatpak if missing, using the system provider."""
        if self.is_available():
            return self._ensure_flathub()
            
        if not self.system_provider:
            console.print("[red]Cannot bootstrap flatpak: No system provider available.[/red]")
            return False

        console.print("[yellow]Flatpak is missing.[/yellow]")
        if not Confirm.ask("Do you want to install flatpak via system packages?"):
            return False

        console.print(f"Installing flatpak using {self.system_provider.name}...")
        if not self.system_provider.install("flatpak"):
            console.print("[red]Failed to install flatpak.[/red]")
            return False

        return self._ensure_flathub()

    def _ensure_flathub(self) -> bool:
        """Ensures flathub remote exists."""
        try:
            res = self._run_cmd(["flatpak", "remote-list"], sudo=False) # User space? Flatpak remotes usually system-wide or user.
            # Let's assume --user for safety or system if sudo? Standard is system usually. 
            # But prompts say "secure". User space is safer. 
            # However professional setup usually implies system-wide for dev tools.
            # Let's try system first, if fails, fallback? 
            # Or just check if 'flathub' text is in output.
            
            if "flathub" in res.stdout:
                return True
                
            console.print("[yellow]Flathub remote missing.[/yellow]")
            if not Confirm.ask("Add flathub remote?"):
                return False
                
            # flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
            self._run_cmd(
                ["flatpak", "remote-add", "--if-not-exists", "flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo"],
                sudo=True # Adding remote typically needs privs unless --user
            )
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to setup flathub: {e}[/red]")
            return False

    def update_indexes(self) -> bool:
        if not self.is_available(): return False
        try:
            # flatpak update --appstream
            self._run_cmd(["flatpak", "update", "--appstream"], sudo=False) # Can be user
            return True
        except subprocess.CalledProcessError:
            return False

    def is_installed(self, package_name: str) -> bool:
        if not self.is_available(): return False
        try:
            # flatpak list --app --columns=application
            res = self._run_cmd(["flatpak", "list", "--app", "--columns=application"])
            return package_name in res.stdout
        except subprocess.CalledProcessError:
            return False

    def install(self, package_name: str) -> bool:
        if not self.is_available():
            if not self.bootstrap():
                return False

        try:
            # flatpak install flathub <app> -y
            self._run_cmd(["flatpak", "install", "flathub", package_name, "-y"], sudo=True) 
            return True
        except subprocess.CalledProcessError:
            return False

    def remove(self, package_name: str) -> bool:
        try:
            self._run_cmd(["flatpak", "uninstall", package_name, "-y"], sudo=True)
            return True
        except subprocess.CalledProcessError:
            return False
