from typing import Optional, Tuple
from .loader import CatalogLoader
from .models import PackageDefinition, Transformation
from ..os_detect import get_os_info

class PackageResolver:
    def __init__(self, loader: CatalogLoader = None):
        self.loader = loader or CatalogLoader()
        self.os_info = get_os_info()

    def resolve(self, pkg_id: str) -> Optional[Transformation]:
        """
        Resolves a generic package ID to a specific Transformation (provider + package name)
        for the current OS/Distro.
        """
        pkg = self.loader.get_package(pkg_id)
        if not pkg:
            return None

        # Check supported OS
        current_os_key = "macos" if self.os_info.is_macos else "linux"
        if current_os_key not in pkg.supported_os:
            return None # Not supported

        # 1. Access OS targets
        # Prioritize distro-specific key if on linux? (e.g. 'ubuntu')
        # os_info.distro contains full string, maybe partial match or key map?
        # For now, simplistic 'linux' or 'macos' fallback.
        
        target = None
        
        if self.os_info.is_linux:
             # Try specific distro keys if we added them in models/yaml
             # Example: if os_info.distro is 'ubuntu', look for 'ubuntu' in targets
             distro_key = self.os_info.distro_id.lower()
             if distro_key in pkg.targets:
                 target = pkg.targets[distro_key]
             elif "linux" in pkg.targets:
                 target = pkg.targets["linux"]
        elif self.os_info.is_macos:
             if "macos" in pkg.targets:
                 target = pkg.targets["macos"]

        return target

    def get_package_details(self, pkg_id: str) -> Optional[PackageDefinition]:
         return self.loader.get_package(pkg_id)
