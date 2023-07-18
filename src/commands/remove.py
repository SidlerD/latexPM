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


    # Remove pkg
    if not hasattr(pkg, "dependents"):
        logger.error(f"Found a node in dependency tree without dependents attribute: {pkg}")
        return
    if len(pkg.dependents) == 0:
        delete_pkg_files(pkg)
        remove_from_tree(pkg)
    elif len(pkg.dependents) > 0:
        # Move pkg in tree from dep_to_remove to first package which depends on it
        dest_dep = pkg.dependents.pop(0)
        dest = LockFile.is_in_tree(dest_dep)

        move_in_tree(dest=dest, node=pkg)


def remove(pkg_id: str):
    dep_node = LockFile.find_by_id(pkg_id)
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