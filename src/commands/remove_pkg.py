from src.core.LockFile import LockFile
from src.models.Dependency import Dependency
import logging
logger = logging.getLogger("default")


def remove_pkg(pkg: Dependency, lock_file: LockFile):
    logger.warning(f"Removing a Package is not supported yet. {pkg} will not be removed, but program will act like it has been")
    pass