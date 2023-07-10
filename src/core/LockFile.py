import json
import os
import logging

from src.models.Dependency import Dependency, DependencyNode, serialize_dependency
from src.API import CTAN
from src.models.Version import Version

from anytree.exporter import JsonExporter
from anytree import Node, findall, LevelOrderIter

logger = logging.getLogger("default")
lock_file_name = 'requirements-lock.json'

# TODO: Add functions for adding/removing/moving a DependencyNode, so that functionality is all in this file
# TODO: Create a class for the normal requirements.json file, since that needs to be updated too. 
class LockFile:

    @staticmethod
    def get_name(): 
        return lock_file_name
    
    @staticmethod
    def get_packages_from_file() -> list[Dependency]:
        logger.info(f"Reading dependencies from {os.path.basename(lock_file_name)}")

        if file_is_empty(lock_file_name):
            logger.info(f"No Dependencies found in {lock_file_name}")
            return []


        tree = LockFile.read_file_as_tree()
        
        return _get_packages_from_tree(tree)
    
    @staticmethod
    def write_tree_to_file( root_node: Node):
        logger = logging.getLogger("default")
        logger.info(f"Writing dependency tree to lock-file at {os.getcwd()}")

        exporter = JsonExporter(indent=2, default=serialize_dependency)
        data = exporter.export(root_node)
        with open(lock_file_name, "w") as f:
            f.write(data)


    @staticmethod
    def read_file_as_tree() -> Node:
        logger.debug("Reading dependency tree from lock-file")
        
        # IF file is empty, create new tree
        if file_is_empty(lock_file_name):
            logger.debug(f"Created new tree because {lock_file_name} is empty")
            return Node('root')
        
        # Read the JSON file
        with open(lock_file_name, "r") as file:
            json_data = json.load(file)
        logger.debug(f"{lock_file_name} read successfully")

        # Construct the tree
        root = Node('root')
        if 'children' in json_data:
            for child_data in json_data["children"]:
                construct_tree(child_data, parent=root)

        logger.debug(f"Tree constructed successfully")
        return root
    
    @staticmethod
    def is_in_tree(dep: Dependency, root: DependencyNode) -> Node:
        # FIXME: Check Assumption: If dep.version is None and we have some version of it installed, then that satisfies dep
        filter = lambda node: (
            type(node) == DependencyNode 
            and (
                node.dep == dep or # Is  the same dependency
                (node.dep.id == dep.id and dep.version == None) # Need version None => Any version is fine 
            )
        )
        prev_occurences = findall(root, filter_= filter)
        if(len(prev_occurences) > 1):
            logger.warning(f"{dep} is in tree {len(prev_occurences)} times")

        return prev_occurences[0] if prev_occurences else None


def construct_tree(data, parent=None):
    dep_info = data['dep']
    dep = Dependency(dep_info["id"], dep_info["name"], Version(dep_info["version"]))
    node = DependencyNode(dep, parent=parent)
    if "children" in data:
        for child_data in data["children"]:
            construct_tree(child_data, parent=node)
    return node

def _get_packages_from_tree(tree: Node):
    return [node.dep for node in LevelOrderIter(tree) if hasattr(node, "dep")]

def file_is_empty(path: str):
    return os.path.exists(path) and os.stat(path).st_size == 0
