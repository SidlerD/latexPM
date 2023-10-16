from src.commands.init import init
import logging
from src.commands.list_packages import list_packages
from src.commands.remove import remove
from src.commands.upgrade import upgrade
from src.commands.upgrade_pkg import upgrade_pkg
from src.commands.build import build
from src.helpers.Logger import make_logger
from src.commands.install import install
from src.commands.install_pkg import install_pkg
from src.core import LockFile


class lpm:
    """Provides all the commands for the package manager, allows for 1:1 mapping from cmd input to functions"""

    def __init__(self, log_debug=False):
        if log_debug:
            self._logger = make_logger("default", logging_level=logging.DEBUG)
        else:
            self._logger = make_logger("default")

    def install_pkg(self, pkg_id: str, version: str = "", accept_prompts: bool = False):
        """Install a specific package, including dependencies"""
        self._logger.info(f"Installing package {pkg_id} {version}")
        install_pkg(pkg_id, version=version, accept_prompts=accept_prompts)

    def install(self):
        """Install all packages as specified in lock-file"""
        self._logger.info(f"Installing dependencies from {LockFile.get_name()}")
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
        self._logger.info("Updating all packages")
        upgrade()

    def list_packages(self, top_level_only=False, tree=False):
        """Print list of all installed packages in current project"""
        list_packages(top_level_only, tree)

    def init(self, docker_image: str = ''):
        """Create a new project: LockFile, Docker for packages"""
        init(docker_image)

    def build(self, args: list):
        """Build tex-files by executing the provided args in the docker container, using the installed packages"""
        build(args)
