




import logging
from src.API import CTAN
from src.commands.install_pkg import install_pkg
from src.commands.remove_pkg import remove_pkg
from src.core import LockFile
from src.models.Dependency import Dependency, DependencyNode
from src.models.Version import Version
from src.helpers.DependenciesHelpers import extract_dependencies
from anytree import Node

logger = logging.getLogger("default")

def _handle_dep(dep: Dependency, root: Node):
    # Get new files from CTAN
    dep_new = CTAN.download_pkg(dep)

    # Get Dependencies of old version from LockFile (i.e direct children of its node)
    dep_old = LockFile.is_in_tree(dep)
    if not dep_old: # TODO: Try to find manually by searching packages folder here
        raise Exception(f"Cannot upgrade {dep}: Is not in Lock-File")
    deps_of_old = [node.dep for node in dep_old.children if hasattr(node, "dep")]
    
    # Get Dependencies of new version of package
    deps_of_new = extract_dependencies(dep_new)
            
    # For each pkg in dep.dependents: Check if they are okay with new version
    # If new package isn't okay, idk what to do: 
    #   Maybe warn error about situation and ask if he wants to disregard this and proceed with new version
    # TODO: Check if any package depends on dep, implement the above


    # For each dependency of new version: Check if old version has same dependencies
    #   If so, remove from both lists
    #   If not, leave in list
    to_install = []
    for d in deps_of_new:
        if d in deps_of_old:
            to_install.append(d)
            deps_of_old.remove(d)

    # For each new_dep in new_list: install_pkg(new_dep)
    for pkg in to_install:
        install_pkg(pkg)

    # For each old_dep in old_list: remove_pkg(old_dep) # This should include checking .dependents
    for pkg in deps_of_old:
        remove_pkg(pkg)

    pass

def upgrade_pkg(pkg_id: str):
    rootNode = None
    try:
        dep = Dependency(pkg_id, CTAN.get_name_from_id(pkg_id))
        rootNode = LockFile.read_file_as_tree()
    
        exists = LockFile.is_in_tree(dep)
        if not exists:
            logger.warning(f"Upgrading {pkg_id} not possible: {pkg_id} not found in {LockFile.get_name()}")
            return
        
        old_version = exists.dep.version if hasattr(exists, 'dep') else Version() #FIXME: What is else case here?
        new_version = CTAN.get_version(pkg_id)
        
        if(old_version == new_version):
            logger.warning(f"{dep} is already in newest version, upgrading not possible")
            return
        
        logger.info(f"Upgrading {pkg_id} from {old_version} to {new_version}")
        _handle_dep(dep, rootNode) 

        LockFile.write_tree_to_file()

    except Exception as e:
        
        logger.error(f"Couldn't upgrade package {pkg_id}: {str(e)}")
        logging.exception(e)
