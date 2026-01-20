import argparse
import sys
import time
import json
from rich.console import Console
from rich.table import Table

from .version import __version__
from .core.installer import Installer
from .core.profiles.loader import ProfileLoader
from .core.exporter import Exporter
from .core.importer import Importer
from .core.state import StateManager
from .core.os_detect import get_os_info
from .core.updater import Updater
from .core.downgrader import Downgrader
from .core.doctor import Doctor
from .core.manual import ManualMode

console = Console()

def main():
    parser = argparse.ArgumentParser(
        description="AutoConfigOSCLI - Professional Environment Automation"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Profiles Group
    profiles_parser = subparsers.add_parser("profiles", help="Manage Profiles")
    profiles_sub = profiles_parser.add_subparsers(dest="subcommand")
    
    # Profiles List
    list_parser = profiles_sub.add_parser("list", help="List available profiles")
    list_parser.add_argument("--tier", help="Filter by tier (lite/mid/full)")
    
    # Profiles Show
    show_parser = profiles_sub.add_parser("show", help="Show profile details")
    show_parser.add_argument("name", help="Profile name")

    # Install
    install_parser = subparsers.add_parser("install", help="Install a specific profile")
    install_parser.add_argument("profile", help="Name of the profile to install")
    install_parser.add_argument("--dry-run", action="store_true", help="Simulate installation without changes")
    install_parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm prompts")

    # Manual
    subparsers.add_parser("manual", help="Interactive package selector")

    # Status
    subparsers.add_parser("status", help="Show system status and installed profiles")

    # Export/Import
    export_parser = subparsers.add_parser("export", help="Export state to JSON")
    export_parser.add_argument("--output", required=True, help="Output JSON file")

    import_parser = subparsers.add_parser("import", help="Import state from JSON")
    import_parser.add_argument("file", help="Input JSON file")

    # Doctor/Update/Downgrade
    subparsers.add_parser("doctor", help="Run diagnostic checks")
    subparsers.add_parser("update", help="Self-update the tool securely")
    downgrade_parser = subparsers.add_parser("downgrade", help="Revert to previous version")
    downgrade_parser.add_argument("--backup", help="Path to JSON backup to restore data")
    
    # Audit
    audit_parser = subparsers.add_parser("audit", help="Run system audit")
    audit_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # WhoAmI
    whoami_parser = subparsers.add_parser("whoami", help="Manage user identity")
    whoami_parser.add_argument("action", nargs="?", default="show", help="show or edit")


    args = parser.parse_args()

    # ... Existing Handlers ...
    
    if args.command == "audit":
        from .core.audit import SystemAuditor
        
        auditor = SystemAuditor()
        data = auditor.run_audit()
        
        if args.json:
            console.print_json(json.dumps(data))
        else:
            table = Table(title="System Audit Report")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("OS System", data["os_system"])
            table.add_row("Distro", f"{data['distro_id']} {data['os_release']}")
            table.add_row("CPU", data["cpu_info"])
            table.add_row("RAM", f"{data['ram_total_gb']} GB")
            table.add_row("Disk Free", f"{data['disk_free_gb']} GB")
            table.add_row("Shell", data["shell"])
            table.add_row("Tools Detected", f"{len(data['detected_tools'])} found")
            
            console.print(table)
            
            if data['detected_tools']:
                console.print(f"[dim]Tools: {', '.join(data['detected_tools'])}[/dim]")

    elif args.command == "whoami":
        from .core.identity import IdentityManager
        im = IdentityManager()
        
        if args.action == "edit":
            im.interactive_edit()
        else:
            ident = im.get_identity()
            from rich.panel import Panel
            
            content = f"""
[bold]Role:[/bold] {ident['role']}
[bold]Level:[/bold] {ident['level']}
[bold]Machine:[/bold] {ident['machine_type']}
[bold]Last Updated:[/bold] {ident.get('updated_at', 'Never')}

[bold]Preferences:[/bold]
{json.dumps(ident['preferences'], indent=2)}

[bold]Notes:[/bold]
{ident['notes']}
"""
            console.print(Panel(content.strip(), title="User Identity", border_style="blue"))

    elif args.command == "profiles":
        loader = ProfileLoader()
        
        if args.subcommand == "list":
            profiles = []
            for name in loader.list_profiles():
                p = loader.load_profile(name)
                if p:
                    if args.tier and p.tier != args.tier:
                        continue
                    profiles.append(p)
            
            table = Table(title="Available Profiles")
            table.add_column("Name", style="cyan")
            table.add_column("Tier", style="magenta")
            table.add_column("Tags", style="green")
            table.add_column("Description")
            
            for p in profiles:
                table.add_row(p.name, p.tier, ", ".join(p.tags), p.description)
            console.print(table)
            
        elif args.subcommand == "show":
            p = loader.load_profile(args.name)
            if not p:
                console.print(f"[red]Profile {args.name} not found[/red]")
            else:
                console.print(f"[bold cyan]Profile: {p.name}[/bold cyan]")
                console.print(f"Tier: {p.tier}")
                console.print(f"Description: {p.description}")
                console.print(f"Packages: {', '.join(p.packages)}")
        
        else:
            profiles_parser.print_help()

    elif args.command == "install":
        installer = Installer()
        installer.install_profile(args.profile, dry_run=args.dry_run, auto_yes=args.yes)

    elif args.command == "status":
        os_info = get_os_info()
        console.print(f"[bold]OS Info:[/bold] {os_info}")
        state = StateManager()
        try:
             pkgs = state.execute_query("SELECT count(*) as c FROM installed_packages")
             count = pkgs[0]['c']
             console.print(f"[bold]Installed Packages:[/bold] {count}")
        except Exception:
            pass

    elif args.command == "manual":
        manual = ManualMode()
        manual.run()
        
    elif args.command == "doctor":
        doc = Doctor()
        doc.run_full_checks()

    elif args.command == "update":
        Updater().perform_update()

    elif args.command == "downgrade":
        Downgrader().downgrade(args.backup)

    elif args.command == "export":
        Exporter().export_data(args.output)
        
    elif args.command == "import":
        Importer().import_data(args.file)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
