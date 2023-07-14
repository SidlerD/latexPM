from src.commands.list_packages import list_packages
from src.commands.remove import remove
from src.commands.upgrade import upgrade
from src.commands.upgrade_pkg import upgrade_pkg
from src.helpers.Logger import make_logger
from src.commands.install import install
from src.commands.install_pkg import install_pkg
from src.core import LockFile


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
        self._logger.info(f"Installing dependencies from {LockFile.get_name}")
        install()

    def remove(self, pkg_id: str):
        """Remove one specific package"""
        self._logger.info(f"Removing {pkg_id}")
        remove(pkg_id)

    def upgrade_pkg(self, pkg_id: str):
        """Upgrade one specific package"""
        self._logger.info(f"Updating {pkg_id}")
        upgrade_pkg(pkg_id)

    def upgrade(self):
        """Upgrade all packages"""
        self._logger.info(f"Updating all packages")
        upgrade()

    def list_packages(self):
        list_packages()

    def freeze(self):
        """Lock dependencies and write current dependencies + versions to file"""
        raise NotImplementedError

    def init(self):
        """Create a new project: Creates new Docker in which packages will live"""
        raise NotImplementedError
