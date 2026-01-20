import subprocess
import os
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .packages import ProviderManager
from .profiles.loader import ProfileLoader, Profile
from .catalog.resolver import PackageResolver, Transformation, PackageDefinition
from .state import StateManager

console = Console()

class Installer:
    def __init__(self):
        self.state = StateManager()
        self.loader = ProfileLoader()
        self.provider_manager = ProviderManager()
        self.resolver = PackageResolver()

    def install_profile(self, profile_name: str, dry_run: bool = False, auto_yes: bool = False) -> bool:
        if not dry_run:
            self.state.init_db()
        
        profile = self.loader.load_profile(profile_name)
        if not profile:
            console.print(f"[red]Error: Profile '{profile_name}' not found.[/red]")
            return False

        console.print(Panel.fit(f"[bold cyan]Profile: {profile.name}[/bold cyan]\n{profile.description}", title="Installation Plan"))

        # 1. Resolve Plan
        plan = self._create_install_plan(profile)
        
        # 2. Show Summary
        self._print_plan_summary(plan)
        
        if not plan['installable']:
            console.print("[yellow]Nothing to install.[/yellow]")
            return True

        if dry_run:
            console.print("[dim]Dry run complete. No changes made.[/dim]")
            return True

        # 3. Confirm
        if not auto_yes:
            if plan['risky_count'] > 0:
                console.print(f"[bold red]WARNING: This plan includes {plan['risky_count']} high-risk components (scripts).[/bold red]")
            
            if not Confirm.ask("Proceed with installation?"):
                 console.print("[red]Aborted.[/red]")
                 return False

        # 4. Execute
        return self._execute_plan(plan)

    def _create_install_plan(self, profile: Profile) -> Dict[str, Any]:
        installable = []
        skipped = []
        unsupported = []
        risky_count = 0
        bootstraps = set()
        
        for pkg_id in profile.packages:
            trans = self.resolver.resolve(pkg_id)
            pkg_def = self.resolver.get_package_details(pkg_id)
            
            if not trans:
                unsupported.append(pkg_id)
                continue
                
            provider = self.provider_manager.get_provider(trans.provider)
            if not provider:
                unsupported.append(f"{pkg_id} (missing provider: {trans.provider})")
                continue
            
            # Check existing
            is_installed = provider.is_installed(trans.package_name)
            
            item = {
                "id": pkg_id,
                "name": pkg_def.display_name if pkg_def else pkg_id,
                "provider_name": provider.name,
                "target_pkg": trans.package_name,
                "risk": pkg_def.risk_level if pkg_def else "low"
            }
            
            if trans.bootstrap_deps:
                for dep in trans.bootstrap_deps:
                    bootstraps.add(dep)
            
            if is_installed:
                skipped.append(item)
            else:
                installable.append(item)
                if getattr(pkg_def, "is_high_risk", False):
                    risky_count += 1
        
        return {
            "installable": installable,
            "skipped": skipped,
            "unsupported": unsupported,
            "risky_count": risky_count,
            "bootstraps": list(bootstraps)
        }

    def _print_plan_summary(self, plan: Dict[str, Any]):
        table = Table(title="Execution Summary")
        table.add_column("Package", style="cyan")
        table.add_column("Action", style="magenta")
        table.add_column("Provider", style="green")
        table.add_column("Details", style="yellow")
        
        for item in plan['installable']:
            details = ""
            if item['risk'] == 'high':
                details = "[bold red]HIGH RISK[/bold red]"
            elif item['risk'] == 'medium':
                details = "[yellow]Medium Risk[/yellow]"
            
            table.add_row(item['name'], "Install", item['provider_name'], details)
            
        for item in plan['skipped']:
            table.add_row(item['name'], "[dim]Skip (Installed)[/dim]", item['provider_name'], "")
            
        for item in plan['unsupported']:
            table.add_row(str(item), "[red]Unsupported[/red]", "-", "OS mismatch")

        console.print(table)
        
        if plan['bootstraps']:
            console.print(f"[blue]Bootstraps required:[/blue] {', '.join(plan['bootstraps'])}")

    def _execute_plan(self, plan: Dict[str, Any]) -> bool:
        # TODO: Handle bootstraps explicitly if needed, but provider might do it.
        # FlatpakProvider handles its own bootstrap.
        
        success = True
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("Installing...", total=len(plan['installable']))
            
            for item in plan['installable']:
                provider = self.provider_manager.get_provider(item['provider_name'])
                progress.update(task, description=f"Installing {item['name']} via {provider.name}...")
                
                if provider.install(item['target_pkg']):
                     console.print(f"[green]✔ Installed {item['name']}[/green]")
                     self._record_package(item['name'], provider.name)
                else:
                     console.print(f"[red]✘ Failed to install {item['name']}[/red]")
                     success = False
                
                progress.advance(task)
        
        return success

    def _record_package(self, name: str, manager: str):
        try:
            self.state.execute_query(
                "INSERT OR IGNORE INTO installed_packages (name, manager) VALUES (?, ?)",
                (name, manager)
            )
        except Exception:
            pass
