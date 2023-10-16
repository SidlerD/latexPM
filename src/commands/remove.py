import logging
import os
import shutil
from anytree import Node, RenderTree, AsciiStyle, LevelOrderGroupIter
import anytree

from src.core import LockFile
from src.models.Dependency import Dependency, DependencyNode

logger = logging.getLogger("default")

def _handle_dep(pkg: DependencyNode):
    # If other package depends on this one, move in tree instead of removing
    if len(pkg.dependents) > 0:
        while len(pkg.dependents) > 0:
            dest_dep_id = pkg.dependents.pop(0)
            try:
                dest = LockFile.find_by_id(dest_dep_id)
                move_in_tree(dest=dest, node=pkg)
                return
            except ValueError as e:
                logger.info(f"Attempted to move {pkg.id} to {dest_dep_id} in tree, but failed: {dest_dep_id} not in tree anymore")
            except anytree.node.exceptions.LoopError:
                logger.info(f"Attempted to move {pkg.id} to {dest_dep_id} in tree, but failed: {dest_dep_id} is a child of {pkg.id}")
                pass 
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


def remove(pkg_id: str, by_user: bool = True):
    """Remove the specified package and its dependencies

    Args:
        pkg_id (str): Id of package to remove
        by_user (bool, optional): Was remove requested by user directly? If True, user will be asked to confirm removal for non-top-level packages. Defaults to True.
    """
    try:
        dep_node = LockFile.find_by_id(pkg_id)
    except ValueError:
        if by_user:
            logger.warn(f"Attempted to remove {pkg_id} which is not installed")
        return 
    
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
    """Delete all files of package from system

    Args:
        dep_node (DependencyNode): Package whose files to delete
    """
    logger.debug(f"Removing files for {dep_node}")

    # Remove folder including its files
    folder = dep_node.dep.path
    if not os.path.exists(folder):
        logger.info(f"Problem while removing {dep_node.id}: {folder} does not exist")
        return
    
    cnt_files = len([file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))])
    shutil.rmtree(folder)

    logger.info(f"Removed {cnt_files} files for {dep_node}")    

def move_in_tree(dest: DependencyNode|Node, node: DependencyNode|Node):
    """Move a node in tree from its current parent to another parent

    Args:
        dest (DependencyNode | Node): New parent of node
        node (DependencyNode | Node): Node to move in tree
    """
    before = str(node.parent)
    node.parent = dest
    logger.info(f"Moved {node.id} from {before} to {node.parent}")

def remove_from_tree(pkg_node: DependencyNode):
    """Remove all references to pkg_node from tree

    Args:
        pkg_node (DependencyNode): Node of package to remove

    Raises:
        Exception: If pkg_node has children
    """
    if len(pkg_node.children) != 0:
        raise Exception("Attempted to remove a node from Tree which still has children")
    
    LockFile.remove_from_dependents(pkg_id=pkg_node.id)

    pkg_node.parent = None