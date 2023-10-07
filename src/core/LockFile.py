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
def get_name():
    return lock_file_name

def exists() -> bool:
    return os.path.exists(lock_file_name)

def create(docker_image: str|None):
    """Create empty lockfile, pass if already exists"""
    global _root

    if os.path.exists(lock_file_name):
        logger.info("Lockfile already exists")
    else:
        logger.info("Creating lock file")
        _root = Node('root', id='root', dependents=[], docker_image=docker_image)
        write_tree_to_file()

def get_docker_image() -> str|None:
    root = read_file_as_tree()
    return root.docker_image if hasattr(root, 'docker_image') else None

def update_image(image_name: str):
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
    logger.info(f"Reading dependencies from {os.path.basename(lock_file_name)}")

    if _file_is_empty(lock_file_name):
        logger.info(f"No Dependencies found in {lock_file_name}")
        return []

    tree = read_file_as_tree()

    return _get_packages_from_tree(tree)


def write_tree_to_file():
    logger.info(f"Writing dependency tree to lock-file at {os.getcwd()}")

    # exporter = JsonExporter(indent=2)
    exporter = JsonExporter(indent=2, default=serialize_dependency)
    data = exporter.export(_root)
    with open(lock_file_name, "w") as f:
        f.write(data)


def read_file_as_tree() -> Node:
    """returns root-node of tree"""
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


def is_in_tree(dep: Dependency, check_ctan_path: str = None) -> DependencyNode:
    """Returns DependencNode that stores dep that is passed as argument, None if not in tree.\n
    Searching is done by id, version is ignored\n
    If check_ctan_path is provided, node with matching ctan_path will be returned"""
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


def find_by_id(pkg_id: str) -> DependencyNode:
    global _root
    _root = read_file_as_tree()
    occurences = findall(_root, filter_=lambda node: hasattr(node, 'id') and node.id == pkg_id or hasattr(node, 'dep') and 'id' in node.dep.alias and node.dep.alias['id'] == pkg_id)

    if len(occurences) > 1:
        logger.warning(f"{pkg_id} is in tree {len(occurences)} times")
    elif len(occurences) == 0:
        raise ValueError(f"{pkg_id} is not in tree")

    return occurences[0] if occurences else None

def remove_from_dependents(pkg_id: str) -> None:
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
