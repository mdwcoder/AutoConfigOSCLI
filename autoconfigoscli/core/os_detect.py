import platform
import distro
import sys

class OSInfo:
    def __init__(self):
        self.system = platform.system()  # 'Darwin' for macOS, 'Linux' for Linux
        self.release = platform.release()
        self.machine = platform.machine()
        self.distro_id = ""
        self.distro_version = ""

        if self.system == "Linux":
            self.distro_id = distro.id()
            self.distro_version = distro.version()
        elif self.system == "Darwin":
            self.distro_id = "macos"
            self.distro_version = platform.mac_ver()[0]
        elif self.system == "Windows":
            self.distro_id = "windows"
            self.distro_version = platform.version()
        else:
            self.distro_id = (self.system or "unknown").lower()
            self.distro_version = self.release

    @property
    def is_macos(self):
        return self.system == "Darwin"

    @property
    def is_linux(self):
        return self.system == "Linux"

    @property
    def is_windows(self):
        return self.system == "Windows"

    def __repr__(self):
        return (f"OSInfo(system={self.system}, distro={self.distro_id}, "
                f"version={self.distro_version}, arch={self.machine})")

def get_os_info() -> OSInfo:
    return OSInfo()
