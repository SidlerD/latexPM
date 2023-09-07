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


def _handle_dep(dep: Dependency, parent: DependencyNode | Node, root: Node, accept_prompts:bool):
    pkgInfo = CTAN.get_package_info(dep.id)
    ctan_path = pkgInfo['ctan']['path'] if 'ctan' in pkgInfo else None

    # If dependency is already installed, warn and return
    existing_node = LockFile.is_in_tree(dep, check_ctan_path=ctan_path)
    if existing_node:
        existing_par = existing_node.parent
        if hasattr(existing_par, 'dependents'):
            existing_node.dependents.append(parent.dep)

        if existing_node.id != dep.id:
            installed_by = f"because {existing_node.id} has the same path on CTAN: {existing_node.dep.ctan_path}"
        elif type(existing_par) == Node:
            installed_by = "as requested by the user"
        else:
            installed_by = "by " + existing_par.ppath
        
        msg = f"""{parent} depends on {dep}, which is already installed {installed_by}"""

        if existing_node.dep.version != dep.version:
            msg += f", but in version {existing_node.dep.version}. Cannot install two different versions of a package."

        logger.info(msg)
        logger.info(f"Skipped install of {dep}")
        return

    # Download package
    downloaded_dep = PackageInstaller.install_specific_package(dep, accept_prompts=accept_prompts)

    node = DependencyNode(downloaded_dep, parent=parent)

    # Extract dependencies of package, download those recursively
    unsatisfied_deps = extract_dependencies(downloaded_dep)

    for child_dep in unsatisfied_deps:
        _handle_dep(child_dep, node, root, accept_prompts)


def install_pkg(pkg_id: str, version: str = "", accept_prompts: bool = False):
    """Installs one specific package and all its dependencies\n"""

    rootNode = None  # Available in except clause
    try:
        # Build dependency-model with needed information
        try:
            name = CTAN.get_name_from_id(pkg_id)
            dep = Dependency(pkg_id, name, version=version)
        except CtanPackageNotFoundError:
            logger.info(f"Cannot find {pkg_id}. Searching in aliases...")
            alias = VPTAN.get_alias_of_package(id=pkg_id)
            alias_id, alias_name = alias['id'], alias['name']
            pkg_id, name = alias['aliased_by']['id'], alias['aliased_by']['name']
            dep = Dependency(pkg_id, name, version=version, alias={'id': alias_id, 'name': alias_name})


        # Download the package files
        rootNode = LockFile.read_file_as_tree()
        _handle_dep(dep, rootNode, rootNode, accept_prompts=accept_prompts)

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
