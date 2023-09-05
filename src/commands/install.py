import logging

from src.core import LockFile
from src.core.PackageInstaller import PackageInstaller
from src.helpers import FileHelper


def install():
    """
    Install packages as specified in lock-file\n
    - Clears package folder first
    - Doesn't look into dependencies of those packages
    - Installs the exact version specified in lock-file
    """
    logger = logging.getLogger("default")

    decision = ""
    while decision not in ['y', 'n']:
        decision = input("Installing from Lockfile means all packages that are currently installed will be removed. Do you want to proceed? [y / n]: ").lower()

    if decision == 'n':
        logger.info("Install aborted due to user decision")
        return

    FileHelper.clear_and_remove_packages_folder()

    try:
        to_install = LockFile.get_packages_from_file()  # returns list of packages with version

        for pkg in to_install:
            PackageInstaller.install_specific_package(pkg)

        # No need to write to LockFile here because I installed exactly what is in LockFile
    except Exception as e:
        logger.error("Error while installing packages from lock-file")
        logger.error(e)
        # TODO: Do I remove all the installed packages here?
