import subprocess
import os
import shlex
import shutil
import requests
from rich.console import Console
from rich.prompt import Confirm
from .base import PackageProvider

console = Console()

class ScriptProvider(PackageProvider):
    @property
    def name(self) -> str:
        return "script"

    def is_available(self) -> bool:
        return True # Always available

    def update_indexes(self) -> bool:
        return True

    def is_installed(self, package_name: str) -> bool:
        # Scripts are hard to check if installed unless we track them manually.
        # For this purpose, we assume 'False' to allow re-running, or we check state?
        # The Installer logic checks state in DB. So we can return False and let Installer manage DB.
        # Or, usually scripts install a binary. The "package_name" in profile could be "url|binary_check"
        return False

    def install(self, package_name: str) -> bool:
        """
        Expects package_name to be a URL or a shell command.
        Security: Must prompt user.
        """
        console.print(f"[bold red]SECURITY WARNING:[/bold red] You are about to run a remote script.")
        console.print(f"Source: {package_name}")
        
        if not Confirm.ask("Do you trust this source and want to execute it?"):
            console.print("[red]Aborted.[/red]")
            return False

        try:
            # Check if it's a URL
            if package_name.startswith("http"):
                 if os.name == "nt":
                     console.print("[red]Remote POSIX shell scripts are not supported on Windows.[/red]")
                     return False
                 # Download and inspect?
                 # Professional: Ask to review?
                 # For CLI speed, we stream to sh? That's dangerous.
                 # We will run it, but we warned the user.
                 
                 # curl -fsSL url | sh
                 shell = shutil.which("sh")
                 curl = shutil.which("curl")
                 if not shell or not curl:
                     console.print("[red]curl and sh are required to run remote scripts.[/red]")
                     return False
                 cmd = f"{shlex.quote(curl)} -fsSL {shlex.quote(package_name)} | {shlex.quote(shell)}"
            else:
                 cmd = package_name

            subprocess.run(cmd, shell=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Script execution failed: {e}[/red]")
            return False

    def remove(self, package_name: str) -> bool:
        console.print("[yellow]Cannot automatically remove script-installed software.[/yellow]")
        return False
