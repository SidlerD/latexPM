import logging
import os
from anytree import Node, RenderTree, AsciiStyle, LevelOrderGroupIter

from src.core import LockFile
from src.models.Dependency import Dependency, DependencyNode

logger = logging.getLogger("default")

def _handle_dep(pkg: DependencyNode):
        
    # Remove its children
    for child in pkg.children:
        _handle_dep(child.dep)
        
    # Remove pkg
    if not hasattr(pkg, "dependents"):
        logger.error(f"Found a node in dependency tree without dependents attribute: {pkg}")
        return
    if len(pkg.dependents) == 0:
        delete_pkg_files(pkg.dep)
        remove_from_tree(pkg)
    elif len(pkg.dependents) > 1:
        # Move pkg in tree from dep_to_remove to first package which depends on it
        dest = pkg.depends[0]
        move_in_tree(dest=dest, node=pkg)


def remove(pkg_id: str):
    dep = LockFile.find_by_id(pkg_id)
    logger.info(f"Removing {pkg_id} and its dependencies")
    _handle_dep(dep)
    logger.info(f"Removed {pkg_id} and its dependencies")
    LockFile.write_tree_to_file()


def delete_pkg_files(dep: Dependency):
    # TODO: Need mapping from package id to files that package includes for this
    # This would mean that when downloading, I need to add a list of files to the lockfile
    # Could also put them in folders named after pkg_id, but that means importing package in tex is weird (e.g. \usepackage(amsmath/amsmath))
    dep_node = LockFile.is_in_tree(dep)

    if not hasattr(dep_node, 'dep') and not hasattr(dep_node.dep, 'files'):
        raise RuntimeError(f"Couldn't find files to delete for {dep}.")

    files = dep_node.dep.files
    for file in files:
            path = os.path.join(dep_node.dep.path, file)
            logger.debug(f"Removing {path}")    
            os.remove(path)


    logger.info(f"Removed {len(files)} files for {dep}")    

def move_in_tree(dest: DependencyNode|Node, node: DependencyNode|Node):
    before = str(node)
    node.parent = dest
    logger.info(f"Moved {node.id} from {before} to {node}")

def remove_from_tree(child):
    if len(child.children) != 0:
        raise Exception("Attempted to remove a node from Tree which still has children")
    
    child.parent = None