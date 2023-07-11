import logging
from anytree import Node, RenderTree, AsciiStyle, LevelOrderGroupIter


from src.core.LockFile import LockFile
from src.models.Dependency import Dependency, DependencyNode

logger = logging.getLogger("default")

def remove(pkg_id: str):
    """
    For each pkg in package's dependencies:
        if pkg.dependents is empty:
            delete pkg
        else:
            dont delete pkg
            Move pkg to child position of pkg.dependents[0]
    """
    dep_node: DependencyNode = LockFile.find_by_id(pkg_id)

    for child in dep_node.children:
        if not hasattr(child, "dependents"):
            logger.error(f"Found a node in dependency tree without dependents attribute: {child}")
            continue
        if len(child.dependents) == 0:
            delete_pkg_files(child.dep)
            remove_from_tree(child)
        elif len(child.dependents) > 1:
            # Move child in tree from dep_to_remove to first package which depends on it
            dest = child.depends[0]
            move_in_tree(src=dep_node, dest=dest, node=child)
    

def delete_pkg_files(dep: Dependency):
    # TODO: Need mapping from package id to files that package includes for this
    # This would mean that when downloading, I need to add a list of files to the lockfile
    # Could also put them in folders named after pkg_id, but that means importing package in tex is weird (e.g. \usepackage(amsmath/amsmath))
    raise NotImplementedError("Not able to delete package files yet")


def move_in_tree(src: DependencyNode|Node, dest: DependencyNode|Node, node: DependencyNode|Node):
    # if node in src.children:
    before = str(node)
    node.parent = dest
    logger.info(f"Moved {node.id} from {before} to {node}")

def remove_from_tree(child):
    if len(child.children) != 0:
        raise Exception("Attempted to remove a node from Tree which still has children")
    
    child.parent = None