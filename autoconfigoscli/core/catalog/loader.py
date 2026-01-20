import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional
from .models import PackageDefinition, Transformation

class CatalogLoader:
    def __init__(self, catalog_path: str = None):
        if catalog_path:
            self.catalog_path = catalog_path
        else:
            # Default to package internal
            self.catalog_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "packages.yaml"
            )
        self.packages: Dict[str, PackageDefinition] = {}
        self.load()

    def load(self):
        if not os.path.exists(self.catalog_path):
            return

        with open(self.catalog_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data or "packages" not in data:
            return

        for pkg_data in data["packages"]:
            pkg_id = pkg_data.get("id")
            if not pkg_id: continue

            targets = {}
            for os_key, target_data in pkg_data.get("targets", {}).items():
                targets[os_key] = Transformation(
                    provider=target_data.get("provider", "system"),
                    package_name=target_data.get("package", pkg_id),
                    bootstrap_deps=target_data.get("deps", []),
                    repo_url=target_data.get("repo")
                )

            self.packages[pkg_id] = PackageDefinition(
                id=pkg_id,
                display_name=pkg_data.get("display_name", pkg_id),
                description=pkg_data.get("description", ""),
                tags=pkg_data.get("tags", []),
                risk_level=pkg_data.get("risk_level", "low"),
                targets=targets,
                supported_os=pkg_data.get("supported_os", ["linux", "macos"])
            )

    def get_package(self, pkg_id: str) -> Optional[PackageDefinition]:
        return self.packages.get(pkg_id)

    def list_packages(self) -> List[PackageDefinition]:
        return list(self.packages.values())
