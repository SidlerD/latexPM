import json
import os

from src.models.Dependency import Dependency, DependencyNode, serialize_dependency
from src.API import CTAN
from src.models.Version import Version

from anytree.exporter import JsonExporter
from anytree import Node

class LockFile:
    @staticmethod
    def get_packages_from_file(file_path: str) -> list[Dependency]:
        print(f"Reading dependencies from {os.path.basename(file_path)}")
        with open(file_path, "r") as f:
            dependency_dict = json.load(f)

        deps = dependency_dict["dependencies"]
        res: list[Dependency] = []

        for key in deps:
            res.append(Dependency(key, CTAN.get_name_from_id(key), deps[key]))

        return res
    
    @staticmethod
    def write_tree_to_file(root_node: Node):
        print("Writing dependency tree to lock-file")

        file_path = "test-lock.json"
        exporter = JsonExporter(indent=2, default=serialize_dependency)
        data = exporter.export(root_node)
        with open(file_path, "w") as f:
            f.write(data)


    @staticmethod
    def read_file_as_tree() -> Node:
        print("Reading dependency tree from lock-file")
        
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


def construct_tree(data, parent=None):
    dep_info = data['dep']
    dep = Dependency(dep_info["id"], dep_info["name"], Version(dep_info["version"]), dep_info["path"])
    node = DependencyNode(dep, parent=parent)
    if "children" in data:
        for child_data in data["children"]:
            construct_tree(child_data, parent=node)
    return node