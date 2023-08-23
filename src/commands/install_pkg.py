import json
import logging
import os
import logging
from anytree import Node, RenderTree, findall, AsciiStyle

from src.core.PackageInstaller import PackageInstaller
from src.core import LockFile
from src.models.Dependency import Dependency, DependencyNode
from src.API import CTAN
from src.helpers.DependenciesHelpers import extract_dependencies
from src.commands.remove import remove
from src.exceptions.download.CTANPackageNotFound import CtanPackageNotFoundError
from src.exceptions.download.DownloadError import DownloadError

logger = logging.getLogger("default")

def _handle_dep(dep: Dependency, parent: DependencyNode | Node, root: Node):
    existing_node = LockFile.is_in_tree(dep)

    # If dependency is already installed, warn and return
    if existing_node:
        existing_par = existing_node.parent
        if hasattr(existing_par, 'dependents'):
            existing_node.dependents.append(parent.dep) 
            
        installed_by = "as requested by the user" if type(existing_par) == Node else "by " + existing_par.ppath
        msg = f"""{parent} depends on {dep}, which is already installed {installed_by}"""

        if existing_node.dep.version != dep.version:
            msg += f", but in version {existing_node.dep.version}. Cannot install two different versions of a package."
        
        logger.warn(msg)
        logger.info(f"Skipped install of {dep}")
        return
    
    # Download package
    downloaded_dep = PackageInstaller.install_specific_package(dep)

    node = DependencyNode(downloaded_dep, parent=parent)

    # Extract dependencies of package, download those recursively
    unsatisfied_deps = extract_dependencies(downloaded_dep) 
    
    for child_dep in unsatisfied_deps:
        _handle_dep(child_dep, node, root)

def install_pkg(pkg_id: str, version: str = ""):
    """Installs one specific package and all its dependencies\n"""
    
    rootNode = None # Available in except clause
    try:
        # Build dependency-model with needed information
        try:
            name = CTAN.get_name_from_id(pkg_id)
            dep = Dependency(pkg_id, name, version=version)
        except CtanPackageNotFoundError as e:
            aliased_by = CTAN.get_alias_of_package(id=pkg_id)
            alias_id = pkg_id
            pkg_id, name = aliased_by['id'], aliased_by['name']
            dep = Dependency(pkg_id, name, version=version, alias = {'id': alias_id, 'name': ''})

        # Check if package is already installed            
        rootNode = LockFile.read_file_as_tree()
        exists = LockFile.is_in_tree(dep)
        if exists:
            logger.warning(f"{pkg_id} is already installed installed at {exists.ppath}{', but in a different version' if exists.dep.version != dep.version else ''}. Skipping install")
            return
        
        # Download the package files
        _handle_dep(dep, rootNode, rootNode) 
        
        LockFile.write_tree_to_file()
        logger.info(f"Installed {pkg_id} and its dependencies")
        
    except Exception as e:
        # Log information
        msg = f"Couldn't install package {pkg_id}: {str(e)}."
        # if rootNode:
        #     msg += f"\nCurrent state: {RenderTree(rootNode, style=AsciiStyle())}"
        # logging.exception(e)
        logger.error(msg)
        logger.info(f"Will remove {pkg_id} and its installed dependencies due to error while installing")

        # Remove installed package + its dependencies which are already installed
        remove(pkg_id, by_user=False)

        