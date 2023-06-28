from src.models.Dependency import Dependency

from src.API import CTAN, TexLive
from src.models.Version import Version

class PackageInstaller:
    @staticmethod
    def install_specific_package(pkg: Dependency):
        pkgInfo = CTAN.get_package_info(pkg.id)
        
        if(pkg.version == None):
            CTAN.download_pkg(pkg, pkgInfo=pkgInfo)
        
        elif "version" in pkgInfo and Version(pkgInfo['version']) == pkg.version:
             # Version to be installed matches version on CTAN
            CTAN.download_pkg(pkg, pkgInfo=pkgInfo)

        else: # Need specific older version => Download from TL
            TexLive.download_pkg(pkg, pkgInfo=pkgInfo)
