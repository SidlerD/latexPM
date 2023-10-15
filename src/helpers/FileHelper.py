

import os
import shutil
from src.core import config
import logging

logger = logging.getLogger("default")

def clear_and_remove_packages_folder():
    """Remove package folder and its contents
    """
    pkg_dir = config.get_package_dir()
    path = os.path.abspath(pkg_dir)

    if os.path.exists(path):
        logger.info(f"Deleting all contents of {path}")
        shutil.rmtree(path)
    else:
        logger.debug(path + ' already removed')