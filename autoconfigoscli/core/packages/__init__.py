from typing import Dict, List, Optional
from ..providers.base import PackageProvider
from ..providers.apt import AptProvider
from ..providers.brew import BrewProvider
from ..providers.dnf import DnfProvider
from ..providers.pacman import PacmanProvider
from ..providers.flatpak import FlatpakProvider
from ..providers.script import ScriptProvider
from ..os_detect import get_os_info

class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, PackageProvider] = {}
        self.system_provider: Optional[PackageProvider] = None
        self._detect_system_provider()
        self._init_providers()

    def _detect_system_provider(self):
        os_info = get_os_info()
        
        # Priority Logic
        potential_providers = []
        if os_info.is_macos:
            potential_providers = [BrewProvider()]
        else:
            potential_providers = [
                AptProvider(),
                DnfProvider(),
                PacmanProvider(),
                BrewProvider()
            ]

        for p in potential_providers:
            if p.is_available():
                self.system_provider = p
                self.providers[p.name] = p
                # If we found a system provider on Linux (non-brew), we prioritize it.
                # If it's brew on linux, it's also fine.
                if p.name != "brew" or os_info.is_macos:
                    break

    def _init_providers(self):
        # Register extensions
        # These might depend on system provider for bootstrapping
        flatpak = FlatpakProvider(system_provider=self.system_provider)
        self.providers[flatpak.name] = flatpak

        script = ScriptProvider()
        self.providers[script.name] = script
        
        # Ensure common aliases or fallbacks?
        # For now, just explicit names.

    def get_provider(self, name: str) -> Optional[PackageProvider]:
        if name == "common" or name == "system":
             # "common" usually maps to system provider
             return self.system_provider
        return self.providers.get(name)

    def get_all_providers(self) -> List[PackageProvider]:
        return list(self.providers.values())
