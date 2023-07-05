




import logging
from src.API import CTAN
from src.core.LockFile import LockFile
from src.models.Dependency import Dependency, DependencyNode
from src.models.Version import Version
from anytree import Node

logger = logging.getLogger("default")

def _handle_dep(dep: Dependency, root: Node):
    # Get new files from CTAN
    # Get Dependencies of old version from LockFile (i.e direct children of its node)
    # Get Dependencies of files
    # For each dependency of new version: Check if old version has same dependencies
    #   If so, remove from both lists
    #   If not, leave in list
    # For each new_dep in new_list: install_pkg(new_dep)
    # For each old_dep in old_list: remove_pkg(old_dep) # THis should include checking .dependents
    # For each pkg in dep.dependents: Check if they are okay with new version
    # If new package isn't okay, idk what to do: 
    #   Maybe warn error about situation and ask if he wants to disregard this and proceed with new version
    pass

def upgrade_pkg(pkg_id: str):
    rootNode = None
    try:
        dep = Dependency(pkg_id, CTAN.get_name_from_id(pkg_id))
        rootNode = LockFile.read_file_as_tree()
    
        exists = LockFile.is_in_tree(dep, rootNode)
        if not exists:
            logger.warning(f"Upgrading {pkg_id} not possible: {pkg_id} not found in {LockFile.get_name()}")
            return
        
        old_version = exists.dep.version if hasattr(exists, 'dep') else Version() #FIXME: What is else case here?
        new_version = CTAN.get_version(pkg_id)
        
        logger.info(f"Upgrading {pkg_id} from {old_version} to {new_version}")
        _handle_dep(dep, rootNode, rootNode) 

        LockFile.write_tree_to_file(rootNode)
        logger.info(info)

    except Exception as e:
        
        logger.error(f"Couldn't upgrade package {pkg_id}: {str(e)}")
        logging.exception(e)
