import os
from os.path import join, isfile
import zipfile
from src.models.Dependency import Dependency, DependencyNode, DownloadedDependency

from src.API import CTAN, VPTAN
from src.models.Version import Version
from src.exceptions.download.DownloadError import DownloadError
import logging

logger = logging.getLogger("default")


class PackageInstaller:
    @staticmethod
    def install_specific_package(pkg: Dependency|DependencyNode, accept_prompts: bool = False) -> DownloadedDependency:
        """Download pkg from CTAN or VPTAN to packages folder, install and organize its files

        Args:
            pkg (Dependency | DependencyNode): Package to install. If type is DependencyNode, use its .dep.url as download-url
            accept_prompts (bool, optional): If True, user will not be prompted for decisions

        Raises:
            DownloadError: Downloaded zip-file cannot be opened

        Returns:
            DownloadedDependency
        """
        pkgInfo = CTAN.get_package_info(pkg.id)
        version_matches = lambda p: "version" in pkgInfo and Version(pkgInfo['version']) == p.version

        # TODO: Add interface for DownloadSources (TL, CTAN) which defines method download_pkg and explains it needs to return DownloadedDependency
        try:
            if hasattr(pkg, 'dep') and hasattr(pkg.dep, 'url'): # Package from Lockfile
                url = pkg.dep.url
                if 'ctan' in url and '.zip' in url: # TODO: Implement better check for CTAN vs VPTAN
                    downloaded_dep = CTAN.download_pkg(pkg.dep, url=url, pkgInfo=pkgInfo)
                else:
                    downloaded_dep = VPTAN.download_pkg(pkg.dep, url=url, pkgInfo=pkgInfo, closest=False)

            elif pkg.version == None or version_matches(pkg): # pkg.version == None instead of is None so that Version.__eq__ is called
                downloaded_dep = CTAN.download_pkg(pkg, pkgInfo=pkgInfo)

            else:  # Need specific older version => Download from VPTAN
                try:
                    downloaded_dep = VPTAN.download_pkg(pkg, pkgInfo=pkgInfo)
                except DownloadError:
                    # Try to install closest version available
                    if not pkg.version.date:  # Can only install closest version with dates
                        raise

                    decision = 'y' if accept_prompts else ''
                    while decision not in ['y', 'n']:
                        decision = input(f"{pkg.id} is not available on VPTAN in version {pkg.version}. Do you want to install the closest later version? [y/n]: ").lower()
                    if decision == 'n':
                        raise

                    logger.info(f"Downloading the closest later version for {pkg} from VPTAN")
                    try:
                        downloaded_dep = VPTAN.download_pkg(pkg, pkgInfo=pkgInfo, closest=True)
                    except DownloadError:
                        # Happens if version extraction always failed on CTAN git archive
                        logger.info(f"VPTAN has no information about {pkg.id}. Downloading from CTAN in newest version")
                        pkg.version = Version()  # Because we now install latest version
                        downloaded_dep = CTAN.download_pkg(pkg, pkgInfo=pkgInfo)


        except zipfile.BadZipFile:
            raise DownloadError(f"Error while downloading zip-file for {os.path.basename(pkg.id)}: Cannot open zip file")

        return downloaded_dep
