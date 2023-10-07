import os
from os.path import isdir, join, abspath
import logging
from anytree import RenderTree, AsciiStyle, LevelOrderIter

from src.core import LockFile, config
from src.models.Dependency import Dependency

logger = logging.getLogger("default")

def list_packages(top_level_only, tree) -> list[Dependency]:
    root = LockFile.read_file_as_tree()
    if not root or hasattr(root, 'children') and len(root.children) == 0:
        print("No packages installed yet")
        return
    
    if tree:
        if top_level_only:
            print(RenderTree(root, maxlevel=2).by_attr(lambda n: n.dep if hasattr(n, 'dep') else n.name))
        else:
            print(RenderTree(root).by_attr(lambda n: n.dep if hasattr(n, 'dep') else n.name))
    
    else:
        if top_level_only:
            deps = [node.dep for node in LevelOrderIter(root, maxlevel=2) if hasattr(node, "dep")]
        else:
            deps = [node.dep for node in LevelOrderIter(root) if hasattr(node, "dep")]
        print('\n'.join(f" - {dep}" for dep in deps))
            


    
# TODO: Move this to function class to use as guard before executing lpm calls
# pkgs_dir = abspath(config.get_package_dir())
# pkgs_in_folder = [elem for elem in os.listdir(pkgs_dir) if isdir(join(pkgs_dir, elem))]

# pkgs_from_lockfile = LockFile.get_packages_from_file()
# pkgs_from_lockfile_names = [dep.name for dep in pkgs_from_lockfile] # As long as I use pkg-name for folder

# pkgs_in_folder.sort()
# pkgs_from_lockfile_names.sort()
# if(pkgs_in_folder != pkgs_from_lockfile_names):
#     logger.error(f"{LockFile.get_name()} and {config.get_package_dir()} are out of Sync! \nPackages in Lockfile: {pkgs_from_lockfile_names}\n Packages in {config.get_package_dir()} folder: {pkgs_in_folder}")
#     raise RuntimeError(f"FATAL: Packages in LockFile differ from those in /{config.get_package_dir()}. ")
#     #TODO: Should try to recover here or give instructions how to recover, e.g. install from LockFile   

# if len(pkgs_from_lockfile) == 0:
#     print("No packages installed currently")
#     return

# if top_level_only:
#     print('\n'.join(f" - {pkg}" for pkg in pkgs_from_lockfile))
