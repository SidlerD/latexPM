import logging
import os
import shutil
from anytree import Node, RenderTree, AsciiStyle, LevelOrderGroupIter

from src.core import LockFile
from src.models.Dependency import Dependency, DependencyNode

logger = logging.getLogger("default")

def _handle_dep(pkg: DependencyNode):
    # Remove its children
    while pkg.children: # While instead of for because during handling children of pkg, pkg.children may change (if pkg depends on pkgB which is installed by its child pkgC, when removing pkgC pkgB becomes child of pkg)
        _handle_dep(pkg.children[0])


    if not hasattr(pkg, "dependents"):
        logger.warn(f"Found a node in dependency tree without dependents attribute: {pkg}")
    
    # Remove pkg
    if not hasattr(pkg, 'dependents') or len(pkg.dependents) == 0:
        delete_pkg_files(pkg)
        remove_from_tree(pkg)
    # Move pkg in tree from dep_to_remove to first package which depends on it
    elif len(pkg.dependents) > 0:
        dest_dep = pkg.dependents.pop(0)
        dest = LockFile.is_in_tree(dest_dep)

        move_in_tree(dest=dest, node=pkg)


def remove(pkg_id: str, by_user: bool = True):
    """Remove package and its dependencies
        by_user: Was remove requested by user directly? If True, user will be asked to confirm removal for non-top-level packages
    """
    dep_node = LockFile.find_by_id(pkg_id)
    # If package was not installed by user directly, warn and ask if he really wants to since it will probably break package that installed it
    if by_user and dep_node.depth > 1: 
        decision = ""
        while decision not in ['y', 'n']:
            decision = input(f"{dep_node.ppath} depends on {pkg_id}. Removing {pkg_id} could lead to {dep_node.parent} not working correctly anymore. Do you want to continue? [y / n]:").lower()
        if(decision == 'n'): 
            logger.info(f"Removing {pkg_id} aborted due to user decision")
            return

    logger.info(f"Removing {pkg_id} and its dependencies")
    _handle_dep(dep_node)
    logger.info(f"Removed {pkg_id} and its dependencies")
    LockFile.write_tree_to_file()


def delete_pkg_files(dep_node: DependencyNode):
    if not hasattr(dep_node, 'dep_node') and not hasattr(dep_node.dep, 'files'):
        raise RuntimeError(f"Couldn't find files to delete for {dep_node.dep}.")

    # Remove folder including its files
    folder = dep_node.dep.path
    cnt_files = len([file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))])
    shutil.rmtree(folder)

    logger.info(f"Removed {cnt_files} files for {dep_node}")    

def move_in_tree(dest: DependencyNode|Node, node: DependencyNode|Node):
    before = str(node.parent)
    node.parent = dest
    logger.info(f"Moved {node.id} from {before} to {node.parent}")

def remove_from_tree(child):
    if len(child.children) != 0:
        raise Exception("Attempted to remove a node from Tree which still has children")
    
    child.parent = None
    # TODO: Remove dep from all .dependents of tree