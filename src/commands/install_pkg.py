import json
import logging
import os
from src.core.PackageInstaller import PackageInstaller

from src.models.Dependency import Dependency, DependencyNode
from src.API import CTAN
from src.core.LockFile import LockFile
from src.helpers.DependenciesHelpers import extract_dependencies

from anytree import Node, RenderTree, findall, AsciiStyle


def _handle_dep(dep: Dependency, parent: DependencyNode | Node, root: Node):
    if LockFile.is_in_tree(dep, root):
        return
    
    try:
        # Download package
        folder_path = PackageInstaller.install_specific_package(dep)
        dep.path = folder_path # Points to the folder of all files of the package
        node = DependencyNode(dep, parent=parent)

        # Extract dependencies of package, download those recursively
        _, unsatisfied_deps = extract_dependencies(dep) 
        for child_dep in unsatisfied_deps:
            try:
                _handle_dep(child_dep, node, root)
            except (ValueError, NotImplementedError) as e :
                print(e)
    
    except (ValueError, NotImplementedError) as e :
        print(f"Problem while installing {dep.id} {dep.version if dep.version else 'None'}: {str(e)}")
        print(RenderTree(root, style=AsciiStyle()))

def install_pkg(pkg_id: str):
    """Installs one specific package and all its dependencies\n
    Returns json to add to requirements-file, describing installed package and dependencies"""
    
    try:
        rootNode = LockFile.read_file_as_tree()

        dep = Dependency(pkg_id, CTAN.get_name_from_id(pkg_id), version="")
        _handle_dep(dep, rootNode, rootNode) 

        LockFile.write_tree_to_file(rootNode)
    except Exception as e:
        # TODO: If error with one package installation, do I need to undo everything or do I leave it and write to lockfile? Id say undo all
        logging.exception(e)
        print(f"Installing package {pkg_id} failed at dependency {dep}")
        print(RenderTree(rootNode, style=AsciiStyle()))
        