import subprocess
from rich.console import Console
from .state import StateManager
from pathlib import Path

console = Console()

class Downgrader:
    def __init__(self):
        self.state = StateManager()
        self.repo_dir = Path.home() / ".autoconfigoscli" / "repo"

    def downgrade(self, backup_json: str = None):
        console.print("[bold yellow]Downgrade Initiated[/bold yellow]")
        
        # 1. Determine Previous Version
        # For now, we rely on git reflog or just HEAD~1 if simplistic
        # Requirement: "Only returns to previously installed version"
        
        # Logic: Check git for previous tag or commit?
        # Simpler professional approach: git checkout HEAD@{1} ?
        # Or look at sqlite history?
        
        # We will use git previous commit for code
        try:
            console.print("Reverting code to previous version...")
            subprocess.run(["git", "checkout", "HEAD^"], cwd=self.repo_dir, check=True)
            console.print("[green]Code reverted.[/green]")
        except subprocess.CalledProcessError:
             console.print("[red]Failed to revert code. Aborting.[/red]")
             return
        
        # 2. Restore Data if backup provided
        if backup_json:
            from .importer import Importer
            importer = Importer()
            importer.import_data(backup_json)
        else:
            console.print("[yellow]No data backup provided. Code is downgraded but DB schema is current.[/yellow]")
            console.print("[dim]Use --backup <file.json> to restore data state.[/dim]")

        console.print("[bold green]Downgrade Complete.[/bold green]")
