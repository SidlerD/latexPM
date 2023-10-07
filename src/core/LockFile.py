import json
import os
import logging

from src.models.Dependency import Dependency, DependencyNode, DownloadedDependency, serialize_dependency
from src.models.Version import Version

from anytree.exporter import JsonExporter
from anytree import Node, findall, LevelOrderIter

logger = logging.getLogger("default")
lock_file_name = 'requirements-lock.json'
_root = None


# TODO: Add functions for adding/removing/moving a DependencyNode, so that functionality is all in this file
# URGENT: Create a class for the normal requirements.json file, since that needs to be updated too.
def get_name() -> str:
    """Get name of lock file

    Returns:
        str: Name of Lock file
    """
    return lock_file_name

def exists() -> bool:
    """Check if lock file already exists

    Returns:
        bool: True if file with name of lockfile exists in cwd
    """
    return os.path.exists(lock_file_name)

def create(docker_image: str|None) -> None:
    """Create empty lockfile, do nothing if it already exists

    Args:
        docker_image (str | None): Docker image to write to lock file
    """
    global _root

    if os.path.exists(lock_file_name):
        logger.info("Lockfile already exists")
    else:
        logger.info("Creating lock file")
        _root = Node('root', id='root', dependents=[], docker_image=docker_image)
        write_tree_to_file()

def get_docker_image() -> str|None:
    """Get name of Docker image specified in lock file

    Returns:
        str|None: Name of Docker Image, None if not specified
    """
    root = read_file_as_tree()
    return root.docker_image if hasattr(root, 'docker_image') else None

def update_image(image_name: str) -> None:
    """Update docker image in Lockfile to image_name

    Args:
        image_name (str): Name of image to write to lockfile
    """
    if not image_name:
        logger.debug("Cannot update LockFile.docker_image with empty image_name")
        return
    
    read_file_as_tree()
    old_image = get_docker_image()
    if old_image:
        decision = '' 
        while decision not in ['y', 'n']:
            decision = input(f"Lockfile specifies {old_image} as docker image. Do you want to overwrite?: ").lower()
        if decision == 'n':
            return
    
    _root.docker_image = image_name
    logger.debug(f"Changed docker-image from {old_image} to {image_name}")
    write_tree_to_file()

def get_packages_from_file() -> list[DependencyNode]:
    """List installed packages

    Returns:
        list[DependencyNode]: List of installed packages
    """
    logger.info(f"Reading dependencies from {os.path.basename(lock_file_name)}")

    if _file_is_empty(lock_file_name):
        logger.info(f"No Dependencies found in {lock_file_name}")
        return []

    tree = read_file_as_tree()

    return _get_packages_from_tree(tree)


def write_tree_to_file() -> None:
    """Persist the tree described by LockFile._root to the file"""
    logger.info(f"Writing dependency tree to lock-file at {os.getcwd()}")

    # exporter = JsonExporter(indent=2)
    exporter = JsonExporter(indent=2, default=serialize_dependency)
    data = exporter.export(_root)
    with open(lock_file_name, "w") as f:
        f.write(data)


def read_file_as_tree() -> Node:
    """Read Tree from lockfile (if not already read), return root-node of tree"""
    global _root
    if _root:
        return _root

    logger.debug("Reading dependency tree from lock-file")

    # IF file is empty, create new tree
    if not os.path.exists(lock_file_name) or _file_is_empty(lock_file_name):
        create(docker_image=None)
        return _root
    
    # Read the JSON file
    with open(lock_file_name, "r") as file:
        json_data = json.load(file)
    logger.debug(f"{lock_file_name} read successfully")

    # Construct the tree
    _root = Node('root', id='root', dependents=[], docker_image=json_data['docker_image'])
    if 'children' in json_data:
        for child_data in json_data["children"]:
            _construct_tree(child_data, parent=_root)

        logger.debug("Tree constructed successfully")

    return _root


def is_in_tree(dep: Dependency, check_ctan_path: str = None) -> DependencyNode|None:
    """Find package by its id in tree, return its node or None if not found

    Args:
        dep (Dependency): Package to find in Tree (Version is ignored)
        check_ctan_path (str, optional): Path of package on CTAN. If provided, \
        may return different package in Tree that has same path on CTAN

    Returns:
        DependencyNode|None: DependencyNode of package in Tree
    """
    global _root
    _root = read_file_as_tree()

    # ASSUMPTION: Don't need to check version equality here since I can't install two versions of one package
    filter = lambda node: (
        (
            hasattr(node, 'dep')
        )
        and (
            (
                node.dep.id == dep.id  # Is  the same dependency
            )
            or
            (
                check_ctan_path and node.dep.ctan_path == check_ctan_path  # Has same download-path on ctan if downloadpath provided
            )
        )

    )
    prev_occurences = findall(_root, filter_=filter)
    if len(prev_occurences) > 1:
        logger.warning(f"{dep} is in tree {len(prev_occurences)} times")

    return prev_occurences[0] if prev_occurences else None

# TODO: Merge this with is_in_tree
def find_by_id(pkg_id: str) -> DependencyNode:
    """Find package by its id in tree, return its node or None if not found

    Args:
        pkg_id (str): Id of package to find

    Raises:
        ValueError: If package with pkg_id not in tree

    Returns:
        DependencyNode: Package that has pkg_id as id or as id of its alias
    """
    global _root
    _root = read_file_as_tree()
    occurences = findall(_root, filter_=lambda node: hasattr(node, 'id') and node.id == pkg_id or hasattr(node, 'dep') and 'id' in node.dep.alias and node.dep.alias['id'] == pkg_id)

    if len(occurences) > 1:
        logger.warning(f"{pkg_id} is in tree {len(occurences)} times")
    elif len(occurences) == 0:
        raise ValueError(f"{pkg_id} is not in tree")

    return occurences[0] if occurences else None

def remove_from_dependents(pkg_id: str) -> None:
    """Remove pkg_id from node.dependents for all nodes in tree

    Args:
        pkg_id (str): Id of package to remove from all dependents
    """
    for node in LevelOrderIter(_root):
        if hasattr(node, 'dependents'):
            if pkg_id in node.dependents:
                node.dependents.remove(pkg_id)
                logger.debug(f"Removed {pkg_id} from {node.id}.dependents")

# TODO: Find out how to do this using anytree-functionality and ending up with a tree of DependencyNodes that have .dep as DownloadedDependency, not dict
def _construct_tree(data, parent=None):
    dep_info = data['dep']
    dep = Dependency(dep_info["id"], dep_info["name"], version=Version(dep_info["version"]), alias=dep_info['alias'])
    downloaded_dep = DownloadedDependency(dep=dep, folder_path=dep_info['path'], download_url=dep_info['url'], ctan_path=dep_info['ctan_path'])
    node = DependencyNode(downloaded_dep, parent=parent, dependents=data['dependents'])
    if "children" in data:
        for child_data in data["children"]:
            _construct_tree(child_data, parent=node)
    return node


def _get_packages_from_tree(tree: Node):
    return [node for node in LevelOrderIter(tree) if hasattr(node, "dep")]


def _file_is_empty(path: str):
    return os.path.exists(path) and os.stat(path).st_size == 0
