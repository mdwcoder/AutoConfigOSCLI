from typing import Dict, Any, List
from ..audit import SystemAuditor
from ..identity import IdentityManager
from .machine import MachineManager
from ..profiles.loader import ProfileLoader
from ..catalog.loader import CatalogLoader
from ..catalog.resolver import PackageResolver

class Explainer:
    def __init__(self):
        self.auditor = SystemAuditor()
        self.identity = IdentityManager()
        self.machine = MachineManager()
        self.profile_loader = ProfileLoader()
        self.catalog_loader = CatalogLoader()
        self.resolver = PackageResolver(self.catalog_loader)

    def explain_system(self) -> Dict[str, Any]:
        """Aggregates all context context data."""
        return {
            "audit": self.auditor.run_audit(),
            "identity": self.identity.get_identity(),
            "machine": self.machine.get_profile()
        }

    def explain_profile(self, profile_name: str) -> Dict[str, Any]:
        """Analyzes a profile's packages regarding the current system."""
        profile = self.profile_loader.load_profile(profile_name)
        if not profile:
            return {"error": "Profile not found"}

        analysis = {
            "profile": {
                "name": profile.name,
                "tier": profile.tier,
                "description": profile.description,
            },
            "packages_analysis": [],
            "summary": {
                "total": 0,
                "supported": 0,
                "unsupported": 0,
                "risky": 0
            }
        }
        
        for pkg_id in profile.packages:
            pkg_info = self.explain_package(pkg_id)
            analysis["packages_analysis"].append(pkg_info)
            
            analysis["summary"]["total"] += 1
            if pkg_info["supported"]:
                analysis["summary"]["supported"] += 1
            else:
                analysis["summary"]["unsupported"] += 1
            
            if pkg_info["risk_level"] in ["high", "medium"]:
                analysis["summary"]["risky"] += 1
                
        return analysis

    def explain_package(self, pkg_id: str) -> Dict[str, Any]:
        pkg = self.catalog_loader.get_package(pkg_id)
        if not pkg:
            return {"id": pkg_id, "found": False}
        
        target = self.resolver.resolve(pkg_id)
        supported = target is not None
        
        return {
            "id": pkg.id,
            "found": True,
            "display_name": pkg.display_name,
            "description": pkg.description,
            "risk_level": pkg.risk_level,
            "supported": supported,
            "provider": target.provider if target else None,
            "package_name": target.package_name if target else None,
            "check": None # check_cmd not currently in Transformation model
        }
