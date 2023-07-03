import json
import os
import logging

from src.models.Dependency import Dependency, DependencyNode, serialize_dependency
from src.API import CTAN
from src.models.Version import Version

from anytree.exporter import JsonExporter
from anytree import Node, findall

logger = logging.getLogger("default")

class LockFile:
    @staticmethod
    def get_packages_from_file(file_path: str) -> list[Dependency]:
        logger = logging.getLogger("default")
        logger.info(f"Reading dependencies from {os.path.basename(file_path)}")

        with open(file_path, "r") as f:
            dependency_dict = json.load(f)

        deps = dependency_dict["dependencies"]
        res: list[Dependency] = []

        for key in deps:
            res.append(Dependency(key, CTAN.get_name_from_id(key), deps[key]))

        return res
    
    @staticmethod
    def write_tree_to_file(root_node: Node):
        logger = logging.getLogger("default")
        logger.info("Writing dependency tree to lock-file")

        file_path = "test-lock.json"
        exporter = JsonExporter(indent=2, default=serialize_dependency)
        data = exporter.export(root_node)
        with open(file_path, "w") as f:
            f.write(data)


    @staticmethod
    def read_file_as_tree() -> Node:
        logger = logging.getLogger("default")
        logger.info("Reading dependency tree from lock-file")
        
        file_path = "test-lock.json"
        # Cannot use anytree.Importer here because I need the tree-nodes to be my custom NodeMixin type
        
        # Read the JSON file
        with open(file_path, "r") as file:
            json_data = json.load(file)

        # Construct the tree
        root = Node('root')
        for child_data in json_data["children"]:
            construct_tree(child_data, parent=root)
        return root

    @staticmethod
    def add_root_pkg(installed: dict):
        pass

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
    dep = Dependency(dep_info["id"], dep_info["name"], Version(dep_info["version"]), dep_info["path"])
    node = DependencyNode(dep, parent=parent)
    if "children" in data:
        for child_data in data["children"]:
            construct_tree(child_data, parent=node)
    return node