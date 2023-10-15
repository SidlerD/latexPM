import logging
import os
import docker

from src.core import Docker, LockFile
from src.core.PackageInstaller import PackageInstaller
from src.helpers import FileHelper


def install():
    """
    Install packages as specified in lock-file
    - Clears package folder first
    - Pulls docker image from Lockfile
    - Doesn't look into dependencies of those packages
    - Installs the exact version specified in lock-file
    """
    logger = logging.getLogger("default")

    # Try to pull the specified image
    lockfile_image = LockFile.get_docker_image()
    if not lockfile_image:
        logger.error("No docker image specified in lock file")
        return
    try:
        Docker.get_image(lockfile_image)
    except docker.errors.ImageNotFound as e:
        logger.error("Invalid docker image in lock file")
        return

    # Clear packages folder
    if os.path.exists('packages') and len(os.listdir('packages')) != 0:
        decision = ""
        while decision not in ['y', 'n']:
            decision = input("Installing from Lockfile means all packages that are currently installed will be removed. Do you want to proceed? [y / n]: ").lower()

        if decision == 'n':
            logger.info("Install aborted due to user decision")
            return

        FileHelper.clear_and_remove_packages_folder()

    try:
        # Get list of all installed packages from Lockfile
        to_install_nodes = LockFile.get_packages_from_file()

        # Install those packages 
        for pkg_node in to_install_nodes:
            downloaded_dep = PackageInstaller.install_specific_package(pkg_node, accept_prompts=True)
            # Change path attr of node in Lockfile since it is now installed in a different location
            pkg_node.dep.path = downloaded_dep.path

        LockFile.write_tree_to_file()
    except Exception as e:
        logger.error("Error while installing packages from lock-file")
        logger.error(e)
        # TODO: Do I remove all the installed packages here?
