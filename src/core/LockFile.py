import json
import os

from src.models.Dependency import Dependency
from src.API import CTAN

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
    def write_tree_to_file(dependency_tree):
        pass

    @staticmethod
    def add_root_pkg(installed: dict):
        pass