from rich.console import Console
from .state import StateManager
from .os_detect import get_os_info
import sys
import shutil

console = Console()

class Doctor:
    def __init__(self):
        self.state = StateManager()

    def run_full_checks(self):
        console.print("[bold]Running System Diagnostic...[/bold]")
        self.run_lite_checks(verbose=True)
        # Add simpler checks or more complex ones here
        
    def run_lite_checks(self, verbose=False) -> bool:
        """Runs fast, non-intrusive checks."""
        status = True
        
        # Check 1: OS
        try:
            get_os_info()
            if verbose: console.print("[green]✔ OS Detection OK[/green]")
        except Exception:
            console.print("[red]✘ OS Detection Error[/red]")
            status = False

        # Check 2: Database
        try:
            with self.state.get_connection() as conn:
                conn.execute("SELECT 1")
            if verbose: console.print("[green]✔ Database Connection OK[/green]")
        except Exception:
            console.print("[red]✘ Database Unreachable[/red]")
            status = False

        # Check 3: Dependencies
        if shutil.which("git") is None:
             console.print("[red]✘ Git not found[/red]")
             status = False
        else:
             if verbose: console.print("[green]✔ Git detected[/green]")

        return status
