import logging

from src.API import CTAN, VPTAN
from src.commands import remove
from src.commands.install_pkg import install_pkg
from src.core import LockFile
from src.exceptions.download.CTANPackageNotFound import \
    CtanPackageNotFoundError
from src.models.Dependency import Dependency, DependencyNode
from src.models.Version import Version

logger = logging.getLogger("default")


def _handle_dep(dep: DependencyNode):

    # TODO: Could/should check if dependents are okay with new version, if so don't need to warn user and ask for input
    # If other packages depend on this package, ask user if he wants to proceed
    if dep.dependents:
        decision = ''
        while decision not in ['y', 'n']:
            decision = input(f"{len(dep.dependents)} packages depend on {dep.id}. Upgrading it might break them. Do you want to continue? [y / n]: ").lower()  # noqa: E501
        if decision == 'n':
            logger.info("Upgrade aborted due to user decision")
            return

    # TODO: Optimize this by comparing dependencies of old and new version,
    #       move identical deps from old version to new version

    # Remove old version
    remove._handle_dep(dep)
    # Install new version
    install_pkg(pkg_id=dep.id, version="", accept_prompts=True)


def upgrade_pkg(pkg_id: str):
    """Upgrade the specified package to its newest version(i.e. the version on CTAN)

    Args:
        pkg_id (str): Id of package to upgrade
    """
    try:
        # Build object modeling package to upgrade
        try:
            name = CTAN.get_name_from_id(pkg_id)
            dep = Dependency(pkg_id, name)
        except CtanPackageNotFoundError:
            logger.info(f"Cannot find {pkg_id}. Searching in aliases...")
            alias = VPTAN.get_alias_of_package(id=pkg_id)
            alias_id, alias_name = alias['id'], alias['name']
            pkg_id, name = alias['aliased_by']['id'], alias['aliased_by']['name']
            dep = Dependency(pkg_id, name, alias={'id': alias_id, 'name': alias_name})

        # Check if package is installed
        node_exists = LockFile.is_in_tree(dep)
        if not node_exists:
            logger.warning(f"Upgrading {pkg_id} not possible: {pkg_id} not found in {LockFile.get_name()}")
            return

        old_version = node_exists.dep.version if hasattr(node_exists, 'dep') else Version()
        new_version = CTAN.get_version(pkg_id)

        # If package already in newest version: Abort
        if old_version == new_version:
            logger.warning(f"{dep} is already in newest version, upgrading not possible")
            return

        # Update package
        logger.info(f"Upgrading {pkg_id} from {old_version} to {new_version}")
        _handle_dep(node_exists)

        # Persist dependency tree
        LockFile.write_tree_to_file()

    except Exception as e:
        logger.error(f"Couldn't upgrade package {pkg_id}: {str(e)}")
