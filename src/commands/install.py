import logging
import os
from src.core.LockFile import LockFile
from src.core.PackageInstaller import PackageInstaller
from src.models.Dependency import Dependency, DependencyNode
from anytree import Node, RenderTree, findall, AsciiStyle

from helpers import download_file, extract_dependencies



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

    except Exception as e:
        logging.exception(e)

