from src.models.Dependency import Dependency

from src.API import CTAN, TexLive
from src.models.Version import Version
from src.exceptions.download.DownloadError import DownloadError

class PackageInstaller:
    @staticmethod
    def install_specific_package(pkg: Dependency):
        pkgInfo = CTAN.get_package_info(pkg.id)
        
        if(pkg.version == None):
            try:
                folder_path = CTAN.download_pkg(pkg, pkgInfo=pkgInfo)
            except DownloadError as e:
                print(f"{type(e).__name__}: {str(e)}")
                folder_path = TexLive.download_pkg(pkg, pkgInfo=pkgInfo)
        
        elif "version" in pkgInfo and Version(pkgInfo['version']) == pkg.version:
             # Version to be installed matches version on CTAN
            folder_path = CTAN.download_pkg(pkg, pkgInfo=pkgInfo)

        else: # Need specific older version => Download from TL
            folder_path = TexLive.download_pkg(pkg, pkgInfo=pkgInfo)

        pkg.path = folder_path
        return folder_path