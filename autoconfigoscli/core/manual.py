import shutil
import subprocess
from typing import List, Optional
from rich.console import Console
from rich.prompt import Confirm
from .packages import ProviderManager
from .catalog.loader import CatalogLoader
from .catalog.resolver import PackageResolver

console = Console()

class ManualMode:
    def __init__(self):
        self.provider_manager = ProviderManager()
        self.loader = CatalogLoader()
        self.resolver = PackageResolver(self.loader)

    def run(self):
        if not self._check_fzf():
            console.print("[yellow]FZF not found. Cannot run interactive mode.[/yellow]")
            return

        candidates = self._get_candidates()
        if not candidates:
             console.print("[yellow]No packages found in catalog.[/yellow]")
             return
             
        selected_ids = self._fzf_select(candidates)
        
        if not selected_ids:
            console.print("No selection.")
            return

        self._install_selected(selected_ids)

    def _check_fzf(self) -> bool:
        if shutil.which("fzf"):
            return True
        
        if Confirm.ask("FZF is missing. Install it for interactive mode?"):
             sys_prov = self.provider_manager.system_provider
             if sys_prov and sys_prov.install("fzf"):
                 return True
        return False

    def _get_candidates(self) -> List[str]:
        # Format: "ID :: Display Name :: Tags"
        pkgs = self.loader.list_packages()
        candidates = []
        for p in pkgs:
            # Filter if supported?
            if not self.resolver.resolve(p.id):
                 # Mark as unsupported in list?
                 candidates.append(f"{p.id} :: {p.display_name} :: [Unsupported]")
            else:
                 candidates.append(f"{p.id} :: {p.display_name} :: {', '.join(p.tags)}")
        return candidates

    def _fzf_select(self, candidates: List[str]) -> List[str]:
        # Using fzf --preview to show description
        # We need to act as a preview server or pass all info.
        # Simple trick: Echo description based on ID?
        # Or just show ID/Desc in main line.
        # Let's try to construct a line that has info, and we parse ID.
        
        input_str = "\n".join(candidates)
        
        # Preview command: grep? 
        # Getting a real preview of description from python data is hard via CLI unless we have a helper script.
        # We will skip complex preview for now and rely on display string.
        
        try:
            cmd = ["fzf", "-m", "--reverse", "--height=40%", "--header=Select packages (Tab for multi-select)"]
            res = subprocess.run(
                cmd,
                input=input_str,
                text=True,
                capture_output=True
            )
            if res.returncode == 0:
                lines = res.stdout.strip().split('\n')
                selected = []
                for line in lines:
                    if not line: continue
                    pkg_id = line.split(" :: ")[0]
                    if "[Unsupported]" in line:
                         console.print(f"[red]Skipping unsupported package: {pkg_id}[/red]")
                         continue
                    selected.append(pkg_id)
                return selected
            return []
        except Exception:
            return []

    def _install_selected(self, pkg_ids: List[str]):
        if not pkg_ids: return
        
        for pkg_id in pkg_ids:
             trans = self.resolver.resolve(pkg_id)
             if not trans:
                 console.print(f"[red]Could not resolve {pkg_id}[/red]")
                 continue
             
             provider = self.provider_manager.get_provider(trans.provider)
             if not provider:
                 console.print(f"[red]Provider {trans.provider} not found for {pkg_id}[/red]")
                 continue
                 
             console.print(f"Installing {pkg_id} via {provider.name}...")
             provider.install(trans.package_name)
