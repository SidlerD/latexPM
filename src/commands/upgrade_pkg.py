




import logging
from src.API import CTAN, VPTAN
from src.commands.install_pkg import install_pkg
from src.commands.remove import remove
from src.core import LockFile
from src.exceptions.download.CTANPackageNotFound import CtanPackageNotFoundError
from src.models.Dependency import Dependency, DependencyNode
from src.models.Version import Version
from src.helpers.DependenciesHelpers import extract_dependencies

logger = logging.getLogger("default")

def _handle_dep(dep: Dependency):
    # Get Dependencies of old version from LockFile (i.e direct children of its node)
    dep_before = LockFile.is_in_tree(dep)
    if not dep_before: 
        raise Exception(f"Cannot upgrade {dep}: Is not in Lock-File")
    deps_of_dep_before = [node.dep for node in dep_before.children if hasattr(node, "dep")]
            
    # TODO: Could / should check if dependents are okay with new version, if so we don't need to warn user and ask for input
    # If other packages depend on this package, ask user if he wants to proceed
    if dep_before.dependents:
        decision = ''
        while decision not in ['y', 'n']:
            decision = input(f"{len(dep_before.dependents)} packages depend on {dep.id}. Upgrading it might break them. Do you want to continue? [y / n]: ").lower()
        if(decision == 'n'): 
            logger.info(f"Upgrade aborted due to user decision")
            return
    
    # Get new files from CTAN
    dep_after = CTAN.download_pkg(dep)
    # Get Dependencies of new version of package
    deps_of_dep_after = extract_dependencies(dep_after)

    # Find packages that need to be installed and aren't already installed by dep before upgrading
    to_install = []
    for d in deps_of_dep_after:
        if d in deps_of_dep_before:
            # TODO: This might not work, since one is type downloadeddep and other just dep
            to_install.append(d)
            deps_of_dep_before.remove(d)

    # For each new_dep in new_list: install_pkg(new_dep)
    for pkg in to_install:
        try:
            install_pkg(pkg)
        except:
            logger.error(f"Couldn't download {pkg}, which is a dependency of {dep_after}. Try manually installing it when currect process is finished")

    # For each old_dep in old_list: remove_pkg(old_dep) # This should include checking .dependents
    for pkg in deps_of_dep_before:
        remove(pkg.id, by_user=False)

    pass

def upgrade_pkg(pkg_id: str):
    """Upgrade the specified package to its newest version(i.e. the version on CTAN)

    Args:
        pkg_id (str): Id of package to upgrade
    """
    try:
        try:
            name = CTAN.get_name_from_id(pkg_id)
            dep = Dependency(pkg_id, name)
        except CtanPackageNotFoundError as e:
            logger.info(f"Cannot find {pkg_id}. Searching in aliases...")
            alias = VPTAN.get_alias_of_package(id=pkg_id)
            alias_id, alias_name = alias['id'], alias['name']
            pkg_id, name = alias['aliased_by']['id'], alias['aliased_by']['name']
            dep = Dependency(pkg_id, name, alias = {'id': alias_id, 'name': alias_name})


        exists = LockFile.is_in_tree(dep)
        if not exists:
            logger.warning(f"Upgrading {pkg_id} not possible: {pkg_id} not found in {LockFile.get_name()}")
            return
        
        old_version = exists.dep.version if hasattr(exists, 'dep') else Version() 
        new_version = CTAN.get_version(pkg_id)
        
        if(old_version == new_version):
            logger.warning(f"{dep} is already in newest version, upgrading not possible")
            return
        
        logger.info(f"Upgrading {pkg_id} from {old_version} to {new_version}")
        _handle_dep(dep) 

        LockFile.write_tree_to_file()

    except Exception as e:
        
        logger.error(f"Couldn't upgrade package {pkg_id}: {str(e)}")
        logging.exception(e)
