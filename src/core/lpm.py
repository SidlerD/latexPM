from src.commands.upgrade_pkg import upgrade_pkg
from src.helpers.Logger import make_logger
from src.commands.install import install
from src.commands.install_pkg import install_pkg
from src.core.LockFile import LockFile

import os

class lpm:
    """Provides all the commands for the package manager, allows for 1:1 mapping from cmd input to functions"""

    def __init__(self):
        self._logger = make_logger("default")
        
    def install_pkg(self, pkg_id: str, version: str = ""):
        """Install a specific package"""
        self._logger.info(f"Installing package {pkg_id} {version}")
        install_pkg(pkg_id, version=version)

    def install(self):
        """Install all packages as specified in lock-file"""
        # TODO: Do I need to remove all installed packages before installing from LockFile?
        self._logger.info(f"Installing dependencies from {LockFile.get_name}")
        install()

    def remove(pkg_id: str):
        """Remove one specific package"""

        """
        For each pkg in package's dependencies:
            if pkg.dependents is empty:
                delete pkg
            else:
                dont delete pkg
                Move pkg to child position of pkg.dependents[0]"""
        pass

    def upgrade_pkg(self, pkg_id: str):
        """Upgrade one specific package"""
        self._logger.info(f"Updating {pkg_id}")
        upgrade_pkg(pkg_id)

    def upgrade(self):
        """Upgrade all packages"""
        pass

    def freeze(self):
        """Lock dependencies and write current dependencies + versions to file"""
        pass

    def init(self):
        """Create a new project: Creates new Docker in which packages will live"""
        pass
