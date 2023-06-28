from src.commands.install import install
from src.commands.install_pkg import install_pkg
from src.core.LockFile import LockFile


#TODO: Always write changes to LockFile
class lpm:
    """Provides all the commands for the package manager, allows for 1:1 mapping from cmd input to functions"""
    def install_pkg(pkg_id: str):
        """Install a specific package"""
        installed = install_pkg(pkg_id)
        LockFile.add_root_pkg(installed)

    def install(file_path: str):
        """Install all packages as specified in lock-file"""
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