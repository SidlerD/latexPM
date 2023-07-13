import os
from os.path import isdir, join, abspath

from src.core import LockFile, config
from src.models.Dependency import Dependency


def list_packages() -> list[Dependency]:
    pkgs_dir = abspath(config.get_package_dir())
    pkgs_in_folder = [elem for elem in os.listdir(pkgs_dir) if isdir(join(pkgs_dir, elem))]

    pkgs_from_lockfile = LockFile.get_packages_from_file()
    pkgs_from_lockfile_names = [dep.name for dep in pkgs_from_lockfile] # As long as I use pkg-name for folder

    pkgs_in_folder.sort()
    pkgs_from_lockfile_names.sort()
    if(pkgs_in_folder != pkgs_from_lockfile_names):
        raise RuntimeError(f"FATAL: Packages in LockFile differ from those in /{config.get_package_dir()}. ")
        #TODO: Should try to recover here or give instructions how to recover, e.g. install from LockFile   
    
    if len(pkgs_from_lockfile) == 0:
        print("No packages installed currently")
    else:
        print('\n'.join(f" - {pkg}" for pkg in pkgs_from_lockfile))
