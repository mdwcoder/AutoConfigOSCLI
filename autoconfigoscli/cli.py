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

    # Profiles User
    user_parser = profiles_sub.add_parser("user", help="Manage User Profiles")
    user_sub = user_parser.add_subparsers(dest="user_command", required=True)
    
    # User List
    user_sub.add_parser("list", help="List user profiles")
    
    # User Create
    create_parser = user_sub.add_parser("create", help="Create new user profile")
    create_parser.add_argument("name", help="Name of new profile")
    
    # User Delete
    delete_parser = user_sub.add_parser("delete", help="Delete user profile")
    delete_parser.add_argument("name", help="Name of profile to delete")
    delete_parser.add_argument("--yes", "-y", action="store_true", help="Confirm deletion")
    
    # User Export
    export_prof = user_sub.add_parser("export", help="Export user profile to JSON")
    export_prof.add_argument("name", help="Profile name")
    export_prof.add_argument("--output", required=True, help="Output JSON file")
    
    # User Import
    import_prof = user_sub.add_parser("import", help="Import user profile from JSON")
    import_prof.add_argument("file", help="Input JSON file")

    # Install
    install_parser = subparsers.add_parser("install", help="Install a specific profile")
    install_parser.add_argument("profile", help="Name of the profile to install")
    install_parser.add_argument("--dry-run", action="store_true", help="Simulate installation without changes")
    install_parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm prompts")
    install_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

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

    # Machine Profile
    machine_parser = subparsers.add_parser("machine", help="Manage machine profile")
    machine_parser.add_argument("action", nargs="?", default="show", help="show, edit, or reset")

    # History
    hist_parser = subparsers.add_parser("history", help="Show decision history")
    hist_parser.add_argument("action", nargs="?", default="list", help="list or show")
    hist_parser.add_argument("id", nargs="?", help="Action ID to show")
    
    # Explain
    explain_parser = subparsers.add_parser("explain", help="Explain system state or profiles")
    explain_sub = explain_parser.add_subparsers(dest="explain_target")
    
    # Explain System
    explain_sub.add_parser("system", help="Explain overall system context")
    
    # Explain Profile
    exp_prof = explain_sub.add_parser("profile", help="Explain a profile")
    exp_prof.add_argument("name", help="Profile name")

    # Explain Package
    exp_pkg = explain_sub.add_parser("package", help="Explain a package")
    exp_pkg.add_argument("id", help="Package ID")

    # Recommend (Phase H)
    rec_parser = subparsers.add_parser("recommend", help="Get profile recommendations")
    rec_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    rec_parser.add_argument("--tier", choices=["lite", "mid", "full"], help="Filter by tier")

    # AI Module (Phase H)
    ai_parser = subparsers.add_parser("ai", help="Hybrid AI Assistant")
    ai_sub = ai_parser.add_subparsers(dest="ai_command")
    
    # AI Config
    ai_config_parser = ai_sub.add_parser("config", help="Configure AI Provider")
    ai_config_sub = ai_config_parser.add_subparsers(dest="ai_config_action")
    ai_prov_set = ai_config_sub.add_parser("provider", help="Manage provider")
    ai_prov_set.add_argument("action", choices=["set", "show"], help="set or show")
    ai_prov_set.add_argument("name", nargs="?", choices=["gemini", "openai", "none"], help="Provider name")
    
    # AI Setup (Wizard)
    ai_sub.add_parser("setup", help="Hybrid Setup Wizard (Local + AI)")
    
    # AI Ask
    ai_ask_parser = ai_sub.add_parser("ask", help="Ask AI for explanation")
    ai_ask_parser.add_argument("query", help="Question about system/profiles")

    # Remote (Phase I)
    rem_parser = subparsers.add_parser("remote", help="Remote SSH Management")
    rem_sub = rem_parser.add_subparsers(dest="remote_command", required=True)
    
    # Remote Common Args
    def add_common_remote(p):
        p.add_argument("target", help="user@host")
        p.add_argument("--port", type=int, default=22)
        p.add_argument("--key", help="SSH Key path")

    # Remote Install
    rem_inst = rem_sub.add_parser("install", help="Bootstrap & Install on remote")
    add_common_remote(rem_inst)
    rem_inst.add_argument("profile", help="Profile to install")
    rem_inst.add_argument("--copy-user-profile", help="Local profile to transfer")
    rem_inst.add_argument("--dry-run", action="store_true", help="Simulate")
    
    # Remote Status
    rem_stat = rem_sub.add_parser("status", help="Get remote status")
    add_common_remote(rem_stat)

    # Remote Audit
    rem_audit = rem_sub.add_parser("audit", help="Get remote audit")
    add_common_remote(rem_audit)
    
    # Remote Doctor
    rem_doc = rem_sub.add_parser("doctor", help="Run remote doctor")
    add_common_remote(rem_doc)



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

    elif args.command == "machine":
        from .core.context.machine import MachineManager
        from rich.prompt import Prompt, Confirm
        from rich.panel import Panel
        mm = MachineManager()
        
        if args.action == "edit":
            curr = mm.get_profile()
            new_type = Prompt.ask("Type", choices=["laptop", "desktop", "server"], default=curr["type"])
            new_usage = Prompt.ask("Usage", choices=["personal", "work", "lab"], default=curr["usage"])
            new_power = Prompt.ask("Power", choices=["low", "mid", "high"], default=curr["power"])
            new_gui = Confirm.ask("Has GUI?", default=curr["gui"])
            new_notes = Prompt.ask("Notes", default=curr["notes"])
            
            if Confirm.ask("Save Machine Profile?"):
                mm.update_profile({
                    "type": new_type, "usage": new_usage, "power": new_power,
                    "gui": new_gui, "notes": new_notes
                })
                console.print("[green]Saved.[/green]")
        
        elif args.action == "reset":
            if Confirm.ask("Reset to detected defaults?"):
                mm.reset_profile()
                console.print("[yellow]Reset to defaults.[/yellow]")
        
        else:
            p = mm.get_profile()
            content = f"""
[bold]Type:[/bold] {p['type']}
[bold]Usage:[/bold] {p['usage']}
[bold]Power:[/bold] {p['power']}
[bold]GUI:[/bold] {"Yes" if p['gui'] else "No"}
[bold]Notes:[/bold] {p['notes']}
"""
            console.print(Panel(content.strip(), title="Machine Profile", border_style="magenta"))

    elif args.command == "history":
        from .core.context.history import HistoryManager
        hm = HistoryManager()
        
        if args.action == "show" and args.id:
            entry = hm.get_details(args.id)
            if not entry:
                console.print(f"[red]Entry {args.id} not found[/red]")
            else:
                console.print(Panel(
                    f"Action: {entry['action_type']}\nResult: {entry['result']}\nTimestamp: {entry['timestamp']}\n\nDetails:\n{json.dumps(entry.get('details',{}), indent=2)}", 
                    title=f"History #{entry['id']}"
                ))
        else:
            recent = hm.get_recent()
            table = Table(title="Decision History")
            table.add_column("ID", justify="right")
            table.add_column("Time")
            table.add_column("Action")
            table.add_column("Target")
            table.add_column("Result")
            
            for r in recent:
                result_color = "green" if r['result'] == "success" else "red"
                table.add_row(
                    str(r['id']), 
                    str(r['timestamp']), 
                    r['action_type'], 
                    r['target'], 
                    f"[{result_color}]{r['result']}[/{result_color}]"
                )
            console.print(table)

    elif args.command == "explain":
        from .core.context.explain import Explainer
        from rich.panel import Panel
        ex = Explainer()
        
        target = args.explain_target
        if target is None:
            target = "system" # Default
            
        if target == "system":
            data = ex.explain_system()
            console.print("[bold underline]System Context[/bold underline]")
            
            # Audit
            audit = data['audit']
            console.print(f"\n[cyan]Audit[/cyan]: {audit['os_system']} {audit['distro_id']} ({audit['cpu_info']})")
            console.print(f"RAM: {audit['ram_total_gb']}GB | Disk Free: {audit['disk_free_gb']}GB")
            
            # Identity
            ident = data['identity']
            console.print(f"\n[blue]Identity[/blue]: {ident['role']} ({ident['level']})")
            
            # Machine
            mach = data['machine']
            console.print(f"\n[magenta]Machine[/magenta]: {mach['type']} ({mach['power']} power)")
            
        elif target == "profile":
            data = ex.explain_profile(args.name)
            if "error" in data:
                console.print(f"[red]{data['error']}[/red]")
            else:
                s = data['summary']
                console.print(Panel(
                    f"Profile: {data['profile']['name']} ({data['profile']['tier']})\n"
                    f"Total Packages: {s['total']}\n"
                    f"Supported: [green]{s['supported']}[/green] | Unsupported: [red]{s['unsupported']}[/red]\n"
                    f"Risky Items: [yellow]{s['risky']}[/yellow]",
                    title="Profile Analysis"
                ))
                
                table = Table()
                table.add_column("Package")
                table.add_column("Support")
                table.add_column("Risk")
                table.add_column("Provider")
                
                for pkg in data['packages_analysis']:
                     supp = "[green]Yes[/green]" if pkg['supported'] else "[red]No[/red]"
                     risk = f"[red]{pkg['risk_level']}[/red]" if pkg['risk_level'] == 'high' else pkg['risk_level']
                     table.add_row(pkg['id'], supp, risk, pkg['provider'] or "-")
                console.print(table)

        elif target == "package":
            data = ex.explain_package(args.id)
            console.print(Panel(
                f"ID: {data['id']}\n"
                f"Name: {data['display_name']}\n"
                f"Supported: {'Yes' if data['supported'] else 'No'}\n"
                f"Risk: {data['risk_level']}\n"
                f"Provider: {data['provider']}\n"
                f"Command: {data['check']}",
                title="Package Detail"
            ))

    elif args.command == "recommend":
        from .core.context.explain import Explainer
        from .core.recommendations.engine import RecommendationEngine
        
        # We reuse Explainer to get context easily
        explainer = Explainer()
        ctx = explainer.explain_system()
        
        engine = RecommendationEngine()
        recs = engine.recommend_profiles(ctx['audit'], ctx['identity'], ctx['machine'])
        
        # Filter by tier if requested
        if args.tier:
            recs = [r for r in recs if r['tier'] == args.tier]
            
        if args.json:
            import json
            console.print_json(json.dumps(recs))
        else:
            if not recs:
                console.print("[yellow]No relevant recommendations found.[/yellow]")
            else:
                table = Table(title="Recommended Profiles")
                table.add_column("Score", justify="right", style="bold")
                table.add_column("Profile", style="cyan")
                table.add_column("Tier", style="magenta")
                table.add_column("Reasons / Warnings")
                
                for r in recs:
                    score_color = "green" if r['score'] > 70 else "yellow" if r['score'] > 40 else "red"
                    
                    details = []
                    if r['reasons']:
                        details.append(f"[green]✓ {', '.join(r['reasons'])}[/green]")
                    if r['warnings']:
                        details.append(f"[red]! {', '.join(r['warnings'])}[/red]")
                        
                    details_str = "\n".join(details)
                    
                    table.add_row(
                        f"[{score_color}]{r['score']}[/{score_color}]",
                        r['profile'],
                        r['tier'],
                        details_str
                    )
                console.print(table)
                console.print("\n[dim]Run 'autoconfigoscli install <profile>' to apply.[/dim]")

    elif args.command == "ai":
        from .core.context.explain import Explainer
        from .ai.manager import AIManager
        from .core.recommendations.engine import RecommendationEngine
        from rich.panel import Panel
        from rich.markdown import Markdown
        from rich.prompt import Confirm
        
        manager = AIManager()
        
        if args.ai_command == "config":
             if args.ai_config_action == "provider":
                 if args.action == "set":
                     if manager.set_provider(args.name):
                         console.print(f"[green]AI Provider set to: {args.name}[/green]")
                     else:
                         console.print(f"[red]Failed to set provider {args.name}[/red]")
                 elif args.action == "show":
                     console.print(f"Current AI Provider: [bold]{manager.get_active_provider_name()}[/bold]")

        elif args.ai_command == "setup":
             console.print(Panel("[bold]AutoConfigOS Hybrid Setup[/bold]", style="cyan"))
             
             # 1. Local Analysis
             with console.status("Running Local Analysis..."):
                 explainer = Explainer()
                 ctx = explainer.explain_system()
                 engine = RecommendationEngine()
                 recs = engine.recommend_profiles(ctx['audit'], ctx['identity'], ctx['machine'])
             
             top_rec = recs[0] if recs else None
             
             # Check for clear winner
             clear_winner = False
             if top_rec:
                 score_gap = 0
                 if len(recs) > 1:
                     score_gap = top_rec['score'] - recs[1]['score']
                 else:
                     score_gap = 100 # ample gap if only one
                 
                 if top_rec['score'] >= 60 and score_gap >= 15:
                     clear_winner = True
             
             if clear_winner:
                 console.print(f"[green]Local Recommendation Engine found a clear match:[/green] [bold]{top_rec['profile']}[/bold]")
                 if top_rec['reasons']:
                     console.print("Reaons:")
                     for r in top_rec['reasons']:
                         console.print(f" - {r}")
                 
                 if not Confirm.ask("Do you want to double-check this with AI?", default=False):
                     console.print(f"\n[bold]Selected:[/bold] {top_rec['profile']}")
                     console.print(f"Run [cyan]autoconfigoscli install {top_rec['profile']}[/cyan] to proceed.")
                     return

             # 2. AI Fallback
             console.print("\n[yellow]Engaging AI for disambiguation/verification...[/yellow]")
             if manager.get_active_provider_name() == "none":
                 console.print("[red]No AI Provider configured. Please set GEMINI_API_KEY or OPENAI_API_KEY.[/red]")
                 console.print("Recommended action based on local engine:")
                 if top_rec:
                      console.print(f" -> {top_rec['profile']} (Score: {top_rec['score']})")
                 return

             with console.status(f"Consulting {manager.get_active_provider_name()}..."):
                 # Inject available profiles into context for AI to choose from
                 ctx['profiles'] = [r['profile'] for r in recs[:5]] # Send top 5 candidates
                 response = manager.recommend(ctx)
             
             if "error" in response:
                 console.print(f"[red]AI Error: {response['error']}[/red]")
             else:
                 console.print(Panel(
                     f"[bold]AI Recommendation:[/bold] {response.get('recommended_profile')}\n\n"
                     f"[white]{response.get('reasoning')}[/white]\n\n"
                     f"[yellow]Risks:[/yellow] {', '.join(response.get('risks', []))}",
                     title="Hybrid Analysis Result",
                     border_style="green"
                 ))
                 if response.get('alternatives'):
                     console.print(f"Alternatives: {', '.join(response.get('alternatives'))}")
                     
        elif args.ai_command == "ask":
             explainer = Explainer()
             ctx = explainer.explain_system()
             request_query = args.query
             
             with console.status("Thinking..."):
                 answer = manager.explain(ctx, request_query)
                 
             console.print(Panel(Markdown(answer), title=f"AI Answer ({manager.get_active_provider_name()})"))
             
    elif args.command == "remote":
        from .core.remote.manager import RemoteManager
        from rich.panel import Panel
        from rich.text import Text
        
        console.print(f"[cyan]Connecting to {args.target}...[/cyan]")
        rman = RemoteManager(port=args.port, key_path=args.key)
        
        if args.remote_command == "install":
             local_prof_path = None
             if args.copy_user_profile:
                 # Resolve local path
                 ploader = ProfileLoader()
                 # Check if exists
                 full_path = os.path.join(ploader.user_profiles_dir, f"{args.copy_user_profile}.yaml")
                 if os.path.exists(full_path):
                     local_prof_path = full_path
                 else:
                     console.print(f"[red]Local profile {args.copy_user_profile} not found.[/red]")
                     return

             with console.status("Running Remote Install (Bootstrap -> Deploy -> Install)..."):
                 res = rman.install_profile(args.target, args.profile, local_prof_path, args.dry_run)
             
             if res["success"]:
                 console.print(Panel(res["stdout"], title="Remote Output", border_style="green"))
                 console.print("[bold green]Remote Install Successful (or Dry-Run completed)[/bold green]")
             else:
                 error_msg = res.get("stderr") or res.get("error") or "Unknown error"
                 console.print(Panel(error_msg, title="Remote Error", border_style="red"))
                 
        elif args.remote_command in ["status", "audit", "doctor"]:
             with console.status(f"Running Remote {args.remote_command}..."):
                 res = rman.run_generic(args.target, args.remote_command, "--json" if args.remote_command == "audit" else "")
             
             if res["success"]:
                 if args.remote_command == "audit":
                     # Pretty print JSON if we can
                     try:
                         console.print_json(res["stdout"])
                     except:
                         console.print(res["stdout"])
                 else:
                     console.print(res["stdout"])
             else:
                 console.print(f"[red]Remote Command Failed:[/red]\n{res['stderr']}")

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
        
        elif args.subcommand == "user":
            from .core.profiles.user_manager import UserProfileManager
            from rich.prompt import Prompt, Confirm
            from .core.manual import ManualMode
            
            manager = UserProfileManager()
            
            if args.user_command == "list":
                profiles = []
                for name in loader.list_profiles():
                    if manager.is_user_profile(name):
                         p = loader.load_profile(name)
                         if p: profiles.append(p)
                
                if not profiles:
                    console.print("No user profiles found.")
                else:
                    table = Table(title="User Profiles")
                    table.add_column("Name", style="cyan")
                    table.add_column("Tier")
                    table.add_column("Packages")
                    table.add_column("Description")
                    for p in profiles:
                        table.add_row(p.name, p.tier, str(len(p.packages)), p.description)
                    console.print(table)
            
            elif args.user_command == "create":
                name = args.name
                if manager.is_builtin(name):
                     console.print(f"[red]Cannot create '{name}': Conflicts with built-in profile[/red]")
                     return
                
                desc = Prompt.ask("Description")
                tier = Prompt.ask("Tier", choices=["lite", "mid", "full"], default="mid")
                
                console.print("[green]Select packages using FZF (TAB to multi-select, ENTER to confirm)[/green]")
                manual = ManualMode()
                if not manual._check_fzf():
                    console.print("[red]FZF required for interactive selection.[/red]")
                    return

                candidates = manual._get_candidates()
                selected_ids = manual._fzf_select(candidates)
                
                if not selected_ids:
                    if not Confirm.ask("No packages selected. Create empty profile?"):
                        return
                
                data = {
                    "description": desc,
                    "tier": tier,
                    "tags": ["user"],
                    "packages": selected_ids
                }
                
                if manager.create(name, data):
                     console.print(f"[bold green]Profile '{name}' created successfully![/bold green]")
            
            elif args.user_command == "delete":
                if args.yes or Confirm.ask(f"Delete profile '{args.name}'?"):
                    if manager.delete(args.name):
                        console.print(f"[green]Deleted {args.name}[/green]")
            
            elif args.user_command == "export":
                # Use manager to load raw then dump to json
                data = manager.load_raw(args.name)
                if not data:
                    console.print(f"[red]Profile {args.name} not found[/red]")
                    return
                
                import json
                export_data = {
                    "meta": {"version": "1.0", "exported_at": time.time(), "type": "user_profile"},
                    "profile": {
                        "name": args.name,
                        "data": data
                    }
                }
                with open(args.output, 'w') as f:
                    json.dump(export_data, f, indent=2)
                console.print(f"[green]Exported to {args.output}[/green]")
            
            elif args.user_command == "import":
                import json
                try:
                    with open(args.file, 'r') as f:
                        imported = json.load(f)
                    
                    if "profile" not in imported:
                        console.print("[red]Invalid profile JSON format[/red]")
                        return
                    
                    # Ask for name or use imported name?
                    name = imported['profile']['name']
                    # Suggest rename if exists?
                    
                    if manager.create(name, imported['profile']['data'], overwrite=False):
                         console.print(f"[green]Imported profile '{name}'[/green]")
                    else:
                         if Confirm.ask(f"Profile '{name}' exists. Overwrite?"):
                             manager.create(name, imported['profile']['data'], overwrite=True)
                             console.print(f"[green]Overwritten profile '{name}'[/green]")

                except Exception as e:
                    console.print(f"[red]Import failed: {e}[/red]")
        
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
