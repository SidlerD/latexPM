from src.models.Dependency import Dependency, DownloadedDependency

from src.API import CTAN, TexLive
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
                return CTAN.download_pkg(pkg, pkgInfo=pkgInfo)
            except DownloadError as e:
                logger.info(f"{pkg.id} is not available on CTAN")
                return TexLive.download_pkg(pkg, pkgInfo=pkgInfo)
        
        elif "version" in pkgInfo and Version(pkgInfo['version']) == pkg.version:
             # Version to be installed matches version on CTAN
            return CTAN.download_pkg(pkg, pkgInfo=pkgInfo)

        else: # Need specific older version => Download from TL
            return TexLive.download_pkg(pkg, pkgInfo=pkgInfo)
