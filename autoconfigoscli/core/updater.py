import subprocess
import os
import sys
from rich.console import Console
from .state import StateManager
from .doctor import Doctor  # Assuming Doctor class exists or will be refactored
from pathlib import Path

console = Console()

class Updater:
    def __init__(self):
        self.state = StateManager()
        self.repo_dir = Path.home() / ".autoconfigoscli" / "repo"

    def perform_update(self) -> bool:
        console.print("[bold cyan]Starting Self-Update...[/bold cyan]")
        
        # 1. Update Code (Git)
        if not self._git_pull():
             console.print("[bold red]Critical Error: Git pull failed. Aborting update.[/bold red]")
             return False
        
        # 2. Update Dependencies (Pip)
        if not self._update_deps():
            console.print("[bold red]Critical Error: Dependencies update failed. Aborting.[/bold red]")
            return False

        # 3. Create Backup
        backup_path = self.state.create_backup()
        if backup_path:
            console.print(f"[green]Backup created at: {backup_path}[/green]")
        else:
            console.print("[yellow]Warning: Could not create backup or DB does not exist yet.[/yellow]")

        # 4. Run Migrations
        try:
             console.print("[cyan]Running Migrations...[/cyan]")
             self.state.init_db() # This triggers MigrationManager
             console.print("[green]Migrations OK.[/green]")
        except Exception as e:
             console.print(f"[bold red]Migration Failed: {e}. Restoring backup logic needed here.[/bold red]")
             return False

        # 5. Doctor Check
        console.print("[cyan]Running Validation (Doctor)...[/cyan]")
        if self._run_doctor():
            console.print("[bold green]Update Completed Successfully![/bold green]")
            return True
        else:
            console.print("[bold yellow]Update finished but Doctor found issues.[/bold yellow]")
            return False

    def _git_pull(self) -> bool:
        console.print("  [dim]Fetching updates from git...[/dim]")
        try:
            # Check if it's a git repo
            if not (self.repo_dir / ".git").exists():
                 console.print("[red]Repo directory is not a git repository.[/red]")
                 return False

            subprocess.run(["git", "fetch"], cwd=self.repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "pull"], cwd=self.repo_dir, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"  [red]Git error: {e}[/red]")
            return False

    def _update_deps(self) -> bool:
        console.print("  [dim]Updating dependencies...[/dim]")
        try:
            # Use current executable (python in venv)
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(self.repo_dir / "requirements.txt"), "--quiet"],
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _run_doctor(self) -> bool:
        doc = Doctor()
        return doc.run_lite_checks()
