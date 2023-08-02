import os
from os.path import join, isfile
from src.models.Dependency import Dependency, DownloadedDependency

from src.API import CTAN, VPTAN
from src.models.Version import Version
from src.exceptions.download.DownloadError import DownloadError
import logging

logger = logging.getLogger("default")

class PackageInstaller:
    @staticmethod
    def install_specific_package(pkg: Dependency) -> DownloadedDependency:
        pkgInfo = CTAN.get_package_info(pkg.id)
        
        # TODO: Add interface for DownloadSources (TL, CTAN) which defines method download_pkg and explains it needs to return DownloadedDependency
        if(pkg.version == None):
            try:
                downloaded_dep = CTAN.download_pkg(pkg, pkgInfo=pkgInfo)
            except DownloadError as e:
                logger.info(f"{pkg.id} is not available on CTAN")
                downloaded_dep = VPTAN.download_pkg(pkg, pkgInfo=pkgInfo)
        
        elif "version" in pkgInfo and Version(pkgInfo['version']) == pkg.version:
             # Version to be installed matches version on CTAN
            downloaded_dep = CTAN.download_pkg(pkg, pkgInfo=pkgInfo)

        else: # Need specific older version => Download from TL
            downloaded_dep = VPTAN.download_pkg(pkg, pkgInfo=pkgInfo)
        downloaded_dep.files = [elem for elem in os.listdir(downloaded_dep.path) if isfile(join(downloaded_dep.path, elem))]
        logger.debug(f"{pkg.id} included {len(downloaded_dep.files)} files in its download")

        return downloaded_dep