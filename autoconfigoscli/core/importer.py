import json
import shutil
import time
from typing import Dict, Any
from rich.console import Console

from .state import StateManager, DB_PATH
from .migration_manager import MigrationManager

console = Console()

class Importer:
    def __init__(self):
        self.state = StateManager()

    def import_data(self, input_path: str):
        # 1. Validation
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            console.print("[red]Error: Invalid JSON file.[/red]")
            return

        if "metadata" not in data or "tables" not in data:
            console.print("[red]Error: Backup structure likely invalid. Missing 'metadata' or 'tables'.[/red]")
            return
        
        # 2. Safety Backup
        console.print("[blue]Creating safety backup before import...[/blue]")
        backup_path = self.state.create_backup()
        if backup_path:
             console.print(f"[dim]Backup at: {backup_path}[/dim]")
        
        # 3. Restore
        try:
            with self.state.get_connection() as conn:
                for table, rows in data["tables"].items():
                    # Handle schema differences if needed, for now exact match or skip
                    try:
                        conn.execute(f"DELETE FROM {table}")
                    except Exception:
                        console.print(f"[yellow]Table {table} not found, skipping clean.[/yellow]")

                    if not rows:
                        continue
                    
                    columns = list(rows[0].keys())
                    placeholders = ",".join(["?"] * len(columns))
                    col_names = ",".join(columns)
                    
                    for row in rows:
                        values = [row[c] for c in columns]
                        conn.execute(
                            f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
                            values
                        )
            
            # 4. Post-Import: Run Migrations to ensure schema is up to date with new code
            self.state.init_db()
            console.print("[green]Import Successful![/green]")

        except Exception as e:
            console.print(f"[bold red]Import Failed: {e}[/bold red]")
            console.print(f"[yellow]You may need to restore manually from {backup_path}[/yellow]")
