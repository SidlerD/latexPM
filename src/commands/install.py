import logging
import os
from src.core.LockFile import LockFile
from src.core.PackageInstaller import PackageInstaller
from src.models.Dependency import Dependency, DependencyNode
from anytree import Node, RenderTree, findall, AsciiStyle




def install(file_path: str):
    """
    Install packages as specified in lock-file\n
    - Doesn't look into dependencies of those packages
    - Installs the exact version specified in lock-file
    """
    try:
        to_install = LockFile.get_packages_from_file(file_path) # returns list of packages with version

        for pkg in to_install:
            PackageInstaller.install_specific_package(pkg)

        # TODO: Do I write to LockFile here? I think yes because installed packages have changed

    except Exception as e:
        logging.exception(e)
        # TODO: Do I remove all the installed packages here?

