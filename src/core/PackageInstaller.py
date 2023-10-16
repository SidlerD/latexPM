import logging
import os
import zipfile

from src.API import CTAN, VPTAN
from src.exceptions.download.DownloadError import DownloadError
from src.models.Dependency import (Dependency, DependencyNode,
                                   DownloadedDependency)
from src.models.Version import Version

logger = logging.getLogger("default")


class PackageInstaller:
    @staticmethod
    def install_specific_package(pkg: Dependency | DependencyNode,
                                 accept_prompts: bool = False, src: str = None) -> DownloadedDependency:
        """Download pkg from CTAN or VPTAN to packages folder, install and organize its files

        Args:
            pkg (Dependency | DependencyNode): Package to install. If type is DependencyNode, \
                use its .dep.url as download-url
            accept_prompts (bool, optional): If True, user will not be prompted for decisions
            src (str, optional): Use to specify which repository to download from: \
                possible values: ['VPTAN', 'CTAN', None]

        Raises:
            DownloadError: Downloaded zip-file cannot be opened

        Returns:
            DownloadedDependency
        """
        pkgInfo = CTAN.get_package_info(pkg.id)
        version_matches = lambda p: "version" in pkgInfo and Version(pkgInfo['version']) == p.version  # noqa: E731

        try:
            # If package is from Lockfile, use lockfile from url to install it
            if hasattr(pkg, 'dep') and hasattr(pkg.dep, 'url'):
                url = pkg.dep.url
                if 'ctan' in url and '.zip' in url:  # TODO: Implement better check for CTAN vs VPTAN
                    downloaded_dep = CTAN.download_pkg(pkg.dep, url=url, pkgInfo=pkgInfo)
                else:
                    downloaded_dep = VPTAN.download_pkg(pkg.dep, url=url, pkgInfo=pkgInfo, closest=False)

            # Download from CTAN if specifically requested
            # or no version or version from CTAN requested
            elif src == 'CTAN' or pkg.version == None or version_matches(pkg):  # noqa: E711
                downloaded_dep = CTAN.download_pkg(pkg, pkgInfo=pkgInfo)

            # Download from VPTAN specifically requested specific version requested
            else:
                try:
                    # Install exact version requested
                    downloaded_dep = VPTAN.download_pkg(pkg, pkgInfo=pkgInfo)
                except DownloadError:
                    # Version not available: Try to install closest version available

                    # Can only install closest version with dates
                    if not pkg.version.date:
                        raise

                    # Ask permission to install closest later version
                    decision = 'y' if accept_prompts else ''
                    while decision not in ['y', 'n']:
                        decision = input(f"{pkg.id} is not available on VPTAN in version {pkg.version}. Do you want to install the closest later version? [y/n]: ").lower()  # noqa: E501
                    if decision == 'n':
                        raise

                    logger.info(f"Downloading the closest later version for {pkg} from VPTAN")
                    try:
                        # Download closest later version from VPTAN
                        downloaded_dep = VPTAN.download_pkg(pkg, pkgInfo=pkgInfo, closest=True)
                    except DownloadError:
                        # Version extraction always failed on CTAN git archive
                        # => Download from CTAN
                        logger.info(f"VPTAN has no information about {pkg.id}. Downloading from CTAN in newest version")  # noqa: E501
                        pkg.version = CTAN.get_version(pkg.id)
                        downloaded_dep = CTAN.download_pkg(pkg, pkgInfo=pkgInfo)

        # Catch exceptions when unpacking zipfile
        # I don't know of anything I could do to fix issue here
        except zipfile.BadZipFile:
            raise DownloadError(f"Error while downloading zip-file for \
                                {os.path.basename(pkg.id)}: Cannot open zip file")

        return downloaded_dep
