
import unittest
import os
import yaml
from autoconfigoscli.core.profiles.loader import ProfileLoader
from autoconfigoscli.core.catalog.loader import CatalogLoader

class TestProfiles(unittest.TestCase):
    def setUp(self):
        self.loader = ProfileLoader()
        self.catalog = CatalogLoader()

    def test_all_profiles_resolve(self):
        """Verify all profiles in profiles/ dir can be loaded and packages exist."""
        profile_dir = self.loader.profiles_dir
        for filename in os.listdir(profile_dir):
            if filename.endswith(".yaml"):
                with self.subTest(profile=filename):
                    name = filename.replace(".yaml", "")
                    profile = self.loader.load_profile(name)
                    self.assertIsNotNone(profile, f"Failed to load {name}")
                    
                    # Verify each package is in catalog
                    for pkg_id in profile.packages:
                        # Handle potential duplicate package inputs? Catalog handles it.
                        # But we just check if ID exists.
                        # Actually profile.packages is a list of IDs.
                        pkg = self.catalog.get_package(pkg_id)
                        self.assertIsNotNone(pkg, f"Package '{pkg_id}' in profile '{name}' not found in catalog")

if __name__ == '__main__':
    unittest.main()
