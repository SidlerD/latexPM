import json
import logging
import os
import logging
from src.core.PackageInstaller import PackageInstaller

from src.models.Dependency import Dependency, DependencyNode
from src.API import CTAN
from src.core.LockFile import LockFile
from src.helpers.DependenciesHelpers import extract_dependencies

from anytree import Node, RenderTree, findall, AsciiStyle

logger = logging.getLogger("default")

def _handle_dep(dep: Dependency, parent: DependencyNode | Node, root: Node):
    existing_node = LockFile.is_in_tree(dep, root)

    if existing_node:
        existing_par = existing_node.parent
        if type(existing_par) is DependencyNode:
            logger.info(f"""{parent} depends on {dep}, which is already installed by {existing_par.dep}. Skipping install.""")
            existing_node.dependents.append(parent.dep) # Not sure if adding parent or parent.dep is smarter here
        elif type(existing_par) is Node and existing_par.name == "root":
            logger.info(f"""{parent} depends on {dep}, which is already installed as requested by the user. Skipping install.""")
            #TODO: When existing_par is removed, parent needs to install dep

        
        return
    
    try:
        # Download package
        downloaded_dep = PackageInstaller.install_specific_package(dep)
        node = DependencyNode(downloaded_dep, parent=parent)

        # Extract dependencies of package, download those recursively
        unsatisfied_deps = extract_dependencies(downloaded_dep) 
        for child_dep in unsatisfied_deps:
            try:
                _handle_dep(child_dep, node, root)
            except (ValueError, NotImplementedError) as e :
                print(e)
    
    except (ValueError, NotImplementedError) as e :
        logging.error(f"Problem while installing {dep.id} {dep.version if dep.version else 'None'}: {str(e)}")
        print(RenderTree(root, style=AsciiStyle()))

def install_pkg(pkg_id: str, lock_file: LockFile, version: str = ""):
    """Installs one specific package and all its dependencies\n
    Returns json to add to requirements-file, describing installed package and dependencies"""
    
    rootNode = None
    try:
        dep = Dependency(pkg_id, CTAN.get_name_from_id(pkg_id), version=version)
        rootNode = lock_file.read_file_as_tree()
    
        exists = LockFile.is_in_tree(dep, rootNode)
        if exists:
            logger.warning(f"{pkg_id} is already installed installed at {exists.path}. Skipping install")
            return
        
        _handle_dep(dep, rootNode, rootNode) 

        lock_file.write_tree_to_file(rootNode)
        logger.info(f"Installed {pkg_id} and its dependencies")

    except Exception as e:
        # TODO: If error with one package installation, do I need to undo everything or do I leave it and write to lockfile? Id say undo all
        logger.error(f"Couldn't install package {pkg_id}: {str(e)}")
        logging.exception(e)
        if(rootNode):
            print(RenderTree(rootNode, style=AsciiStyle()))
        