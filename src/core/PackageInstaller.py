import os
from os.path import join, isfile
import zipfile
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
        try:
            version_matches = "version" in pkgInfo and Version(pkgInfo['version']) == pkg.version
            
            if pkg.version == None or version_matches:
                downloaded_dep = CTAN.download_pkg(pkg, pkgInfo=pkgInfo)

            else: # Need specific older version => Download from VPTAN
                downloaded_dep = VPTAN.download_pkg(pkg, pkgInfo=pkgInfo)
        
        except zipfile.BadZipFile:
            raise DownloadError(f"Error while downloading zip-file for {os.path.basename(pkg.id)}: Cannot open zip file")
        

        downloaded_dep.files = [elem for elem in os.listdir(downloaded_dep.path) if isfile(join(downloaded_dep.path, elem))]
        logger.debug(f"{pkg.id} included {len(downloaded_dep.files)} files in its download")

        return downloaded_dep