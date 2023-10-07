




import logging
from src.core import LockFile
from src.commands.upgrade_pkg import upgrade_pkg

logger = logging.getLogger("default")

def upgrade():
    """Upgrade all installed packages to newest version
    """
    failed_deps = []
    all_deps = LockFile.get_packages_from_file()

    for dep in all_deps:
        try:
            upgrade_pkg(dep.id)
        except Exception as e:
            failed_deps.append(dep)
            logger.warning(f"Was not able to upgrade {dep.id}. Will skip to next one ({e})")
    
    if(len(failed_deps) > 0):
        logger.info(f"Upgraded {len(all_deps) - len(failed_deps)} of {len(all_deps)} packages")