import logging
from anytree import Node

from src.core.PackageInstaller import PackageInstaller
from src.core import LockFile
from src.models.Dependency import Dependency, DependencyNode
from src.API import CTAN, VPTAN
from src.helpers.DependenciesHelpers import extract_dependencies
from src.commands.remove import remove
from src.exceptions.download.CTANPackageNotFound import CtanPackageNotFoundError

logger = logging.getLogger("default")


def _handle_dep(dep: Dependency, parent: DependencyNode | Node, root: Node, accept_prompts:bool, src:str):
    pkgInfo = CTAN.get_package_info(dep.id)
    ctan_path = pkgInfo['ctan']['path'] if 'ctan' in pkgInfo else None

    # If dependency is already installed, warn and return
    existing_node = LockFile.is_in_tree(dep, check_ctan_path=ctan_path)
    newer_than = lambda dateA, dateB: dateA and dateB and dateA > dateB
   
    # If version to install newer than installed version, remove installed version
    if existing_node and newer_than(dep.version.date, existing_node.dep.version.date):
        # If version to install > installed version, version to install will 
        # satisfy every requirepackage{}[installed_version], according to syntax of date in \requirepackage
        # Therefore, remove installed version and install the newer requested version.
        logger.info(f"{dep.id} is installed in version {existing_node.dep.version}." \
                    f" Requested install in version {dep.version}." \
                    f" Installing  in {dep.version} because it is newer")
        remove(pkg_id=dep.id, by_user=False)
    # If already installed in equal-or-newer version: Don't install
    elif existing_node:
        existing_par = existing_node.parent

        if hasattr(existing_node, 'dependents'):
            if existing_node.parent.id != parent.id:
                existing_node.add_dependent(parent.id)
        
        # Build message to show to user
        if existing_node.id != dep.id:
            installed_by = f"because {existing_node.id} has the same path on CTAN: {existing_node.dep.ctan_path}"
        elif type(existing_par) == Node:
            installed_by = "as requested by the user"
        else:
            installed_by = "by " + existing_par.ppath
        
        msg = f"""{'root' if parent.id == 'root' else parent} depends on {dep}, which is already installed {installed_by}"""

        if existing_node.dep.version and dep.version and existing_node.dep.version != dep.version:
            msg += f", but in version {existing_node.dep.version}. Cannot install two different versions of a package."

        logger.info(msg)
        logger.info(f"Skipped install of {dep}")
        return

    # Download package 
    downloaded_dep = PackageInstaller.install_specific_package(dep, accept_prompts=accept_prompts, src=src)

    # Add package to tree
    node = DependencyNode(downloaded_dep, parent=parent)

    # Extract dependencies of package
    unsatisfied_deps = extract_dependencies(downloaded_dep)

    # Download those dependencies recursively
    for child_dep in unsatisfied_deps:
        try:
            _handle_dep(child_dep, node, root, accept_prompts, src=src)
        except CtanPackageNotFoundError as e:
            logger.error(f"{str(e)}: Skipping install of {child_dep.id}. If problems arise, install manually")


def install_pkg(pkg_id: str, version: str = "", accept_prompts: bool = False, src: str = None):
    """Installs one specific package and all its dependencies\n

    Args:
        pkg_id (str): Id of package to install
        version (str, optional): String containing version of package to install
        accept_prompts (bool, optional): If True, user will not be prompted\
             about decisions during install of package and dependencies
        src (str, optional): Use to specify which repository to download from: possible values: ['VPTAN', 'CTAN', None]
    """

    try:
        # Build dependency-model with needed information
        try:
            name = CTAN.get_name_from_id(pkg_id)
            dep = Dependency(pkg_id, name, version=version)
        except CtanPackageNotFoundError:
            # Try to find package that aliases this package
            logger.info(f"Cannot find {pkg_id}. Searching in aliases...")
            alias = VPTAN.get_alias_of_package(id=pkg_id)
            alias_id, alias_name = alias['id'], alias['name']
            pkg_id, name = alias['aliased_by']['id'], alias['aliased_by']['name']
            dep = Dependency(pkg_id, name, version=version, alias={'id': alias_id, 'name': alias_name})

        # Download the package files and all its dependencies
        rootNode = LockFile.read_file_as_tree()
        _handle_dep(dep, rootNode, rootNode, accept_prompts=accept_prompts, src=src)

        # Persist dependency-tree in lockfile
        LockFile.write_tree_to_file()
        logger.info(f"Installed {pkg_id} and its dependencies")

    except Exception as e:
        # Log information
        logger.error(f"Couldn't install package {pkg_id}: {str(e)}.")
        logger.info(f"Will remove {pkg_id} and its installed dependencies due to error while installing")

        # Remove installed package + its dependencies which are already installed
        remove(pkg_id, by_user=False)
