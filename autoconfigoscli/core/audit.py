import platform
import shutil
import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List

# Try importing distro/psutil if available (from venv)
try:
    import distro
except ImportError:
    distro = None

try:
    import psutil
except ImportError:
    psutil = None

from .os_detect import get_os_info
from .state import StateManager
from .catalog.loader import CatalogLoader
from .catalog.resolver import PackageResolver

class SystemAuditor:
    def __init__(self):
        self.state = StateManager()
        self.catalog = CatalogLoader()
        self.resolver = PackageResolver(self.catalog)

    def run_audit(self) -> Dict[str, Any]:
        """Collects system data, persists it, and returns the report."""
        self.state.init_db()
        
        info = self._collect_info()
        self._save_audit(info)
        return info

    def _collect_info(self) -> Dict[str, Any]:
        os_info = get_os_info()
        
        # Hardware (Basic fallback if psutil missing)
        ram_gb = 0.0
        if psutil:
            ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        else:
            # Linux fallback for RAM
            if os_info.is_linux and os.path.exists('/proc/meminfo'):
                 try:
                     with open('/proc/meminfo', 'r') as f:
                         for line in f:
                             if 'MemTotal' in line:
                                 kb = int(line.split()[1])
                                 ram_gb = round(kb / (1024**2), 2)
                                 break
                 except: pass

        # Disk
        disk_free_gb = 0.0
        try:
            total, used, free = shutil.disk_usage("/")
            disk_free_gb = round(free / (1024**3), 2)
        except: pass

        # CPU
        cpu_info = platform.processor()
        if os_info.is_linux and not cpu_info:
             # Try getting model name from /proc/cpuinfo
             try:
                 with open('/proc/cpuinfo') as f:
                     for line in f:
                         if "model name" in line:
                             cpu_info = line.split(":")[1].strip()
                             break
             except: pass
        if not cpu_info:
             cpu_info = f"{platform.machine()} ({os.cpu_count()} cores)"

        # Detected Tools
        detected = []
        for pkg in self.catalog.list_packages():
            trans = self.resolver.resolve(pkg.id)
            if not trans: continue
            
            # Check detection via shutil.which directly for the command? 
            # Or use provider check? Provider check is more accurate but slower?
            # For audit, 'which' is fast.
            # Most tools ID matches binary name roughly, or logic needed.
            # Let's use the transformation package name or analyze ID.
            # Actually provider.is_installed() is best but requires instantiating many providers.
            # Let's stick to simple `which` on package name or ID.
            
            check_name = trans.package_name.split()[0] # Handle arguments like "curl ... | sh"
            if " " in trans.package_name:
                 # risky script block, can't detect easily unless we know binary name.
                 # Fallback to ID.
                 check_name = pkg.id
            
            if shutil.which(check_name) or shutil.which(pkg.id):
                detected.append(pkg.id)

        return {
            "os_system": os_info.system,
            "os_release": os_info.release,
            "distro_id": os_info.distro_id,
            "cpu_info": cpu_info,
            "ram_total_gb": ram_gb,
            "disk_free_gb": disk_free_gb,
            "shell": os.environ.get("SHELL", "unknown"),
            "detected_tools": detected
        }

    def _save_audit(self, info: Dict[str, Any]):
        try:
            self.state.execute_query("""
                INSERT INTO system_audits (
                    os_system, os_release, distro_id, cpu_info, 
                    ram_total_gb, disk_free_gb, shell, detected_tools
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                info['os_system'], info['os_release'], info['distro_id'], info['cpu_info'],
                info['ram_total_gb'], info['disk_free_gb'], info['shell'],
                json.dumps(info['detected_tools'])
            ))
        except Exception as e:
            logging.error(f"Failed to save audit: {e}")
