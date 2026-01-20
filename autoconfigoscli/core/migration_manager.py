import sqlite3
import importlib.util
from pathlib import Path
from typing import List, Optional
from rich.console import Console

MIGRATIONS_PATH = Path(__file__).parent.parent / "migrations"
console = Console()

class MigrationManager:
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection

    def get_current_version(self) -> int:
        self.conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")
        
        cur = self.conn.execute("SELECT version FROM schema_version")
        row = cur.fetchone()
        if not row:
            # Check for legacy state (tables exist but no version)
            try:
                self.conn.execute("SELECT 1 FROM installed_packages LIMIT 1")
                # Tables exist, assume version 1 (or 2 if we had more history, but 1 is safe base)
                # Actually Phase A had migration 001. So if tables exist, we are at least at 1.
                # Phase B assumed 1. Phase E adds 3. Wait, where is 2? 
                # There is no 002? If no 002 file, then 1->3 is fine.
                initial_ver = 1
            except sqlite3.OperationalError:
                 initial_ver = 0
            
            self.conn.execute("INSERT INTO schema_version (version) VALUES (?)", (initial_ver,))
            return initial_ver
        return row[0]

    def set_version(self, version: int):
        self.conn.execute("UPDATE schema_version SET version = ?", (version,))
        self.conn.commit()

    def run_migrations(self):
        """Discovers and runs pending migrations."""
        current_ver = self.get_current_version()
        migration_files = sorted(MIGRATIONS_PATH.glob("*.py"))
        
        migrated = False
        for mig_file in migration_files:
            try:
                # 001_initial.py -> 1
                version_num = int(mig_file.name.split('_')[0])
            except ValueError:
                continue

            if version_num > current_ver:
                self._apply_migration(mig_file, version_num)
                migrated = True

        return migrated

    def _apply_migration(self, mig_file: Path, version: int):
        console.print(f"[bold blue]Applied Migration:[/bold blue] {mig_file.name}...")
        
        spec = importlib.util.spec_from_file_location("migration_mod", mig_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'up'):
                try:
                    module.up(self.conn)
                    self.set_version(version)
                    console.print(f"[green]Migration {version} SUCCESS[/green]")
                except Exception as e:
                    console.print(f"[bold red]Migration {version} FAILED: {e}[/bold red]")
                    raise
