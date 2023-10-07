import os
from os.path import isdir, join, abspath
import logging
from anytree import RenderTree, AsciiStyle, LevelOrderIter

from src.core import LockFile, config
from src.models.Dependency import DependencyNode

logger = logging.getLogger("default")

def list_packages(top_level_only: bool, tree: bool) -> list[DependencyNode]:
    """List all installed package

    Args:
        top_level_only (bool): (Only applies to print, not return value!) Only list the packages directly installed by the user, without their dependencies
        tree (bool): (Only applies to print, not return value!) Print packages in dependency-tree format

    Returns:
        list[DependencyNode]: Ignores passed parameters, will always return ALL installed packages
    """
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
            
    return LockFile.get_packages_from_file()
