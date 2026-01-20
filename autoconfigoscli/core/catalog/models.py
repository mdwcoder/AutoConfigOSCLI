from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class PackageStartCmd:
    cmd: str
    args: List[str] = field(default_factory=list)

@dataclass
class Transformation:
    """Represents how to install a package on a specific system."""
    provider: str  # e.g., 'apt', 'brew', 'flatpak', 'script'
    package_name: str  # The actual name in that provider, e.g., 'python3' vs 'python'
    bootstrap_deps: List[str] = field(default_factory=list) # e.g., ['flatpak']
    repo_url: Optional[str] = None # For scripts or custom repos

@dataclass
class PackageDefinition:
    id: str
    display_name: str
    description: str
    tags: List[str] = field(default_factory=list)
    risk_level: str = "low" # low, medium, high
    
    # OS specific mappings
    # Key: 'linux', 'macos' or specific distro like 'ubuntu'
    # Value: Transformation object or dict (for parsing)
    targets: Dict[str, Transformation] = field(default_factory=dict)
    
    # Constraints
    supported_os: List[str] = field(default_factory=lambda: ["linux", "macos"])
    
    @property
    def is_high_risk(self) -> bool:
        return self.risk_level == "high"
