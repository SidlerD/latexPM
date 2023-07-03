from src.helpers.Logger import make_logger
from src.commands.install import install
from src.commands.install_pkg import install_pkg
from src.core.LockFile import LockFile

import os

class lpm:
    """Provides all the commands for the package manager, allows for 1:1 mapping from cmd input to functions"""

    def __init__(self):
        self._logger = make_logger("default")
        
    def install_pkg(self, pkg_id: str):
        """Install a specific package without a version"""
        self._logger.info(f"Installing package {pkg_id}")
        installed = install_pkg(pkg_id)

    def install(self, file_path: str):
        """Install all packages as specified in lock-file"""
        self._logger.info(f"Installing dependencies from lockfile {os.path.basename(file_path)}")
        install(file_path)

    def remove(pkg_id: str):
        """Remove one specific package"""
        pass

    def upgrade_pkg(pkg_id: str):
        """Upgrade one specific package"""
        pass

    def upgrade():
        """Upgrade all packages"""
        pass

    def freeze():
        """Lock dependencies and write current dependencies + versions to file"""
        pass