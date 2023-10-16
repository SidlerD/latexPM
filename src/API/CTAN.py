import requests
import logging
from functools import cache

from src.models.Dependency import Dependency, DownloadedDependency
from src.helpers.DownloadHelpers import download_and_extract_zip
from src.exceptions.download.CTANPackageNotFound import CtanPackageNotFoundError
from src.models.Version import Version

_ctan_url = "https://www.ctan.org/"
logger = logging.getLogger("default")

@cache
def get_id_from_name(name: str) -> str:
    """Get the id of a package on CTAN based on its name

    Args:
        name (str): name of package

    Raises:
        CtanPackageNotFoundError: If name is not a valid name of package on CTAN

    Returns:
        id (str): id of package
    """
    all = requests.get(f"{_ctan_url}json/2.0/packages").json()
    for pkg in all:
        if pkg['name'] == name:
            return pkg['key']
    raise CtanPackageNotFoundError(f"CTAN has no information about package with name {name}")

@cache
def get_name_from_id(id: str) -> str:
    """Get the name of a package on CTAN based on its Id

    Args:
        id (str): Id of package

    Raises:
        CtanPackageNotFoundError: If Id is not a valid ID of package on CTAN

    Returns:
        name (str): Name of package
    """
    res = get_package_info(id)
    if "id" in res:
        return res['name']
    raise CtanPackageNotFoundError("CTAN has no information about package with id " + id)

@cache
def get_package_info(id: str):
    """Returns CTAN's response for endpoint /packages called with id

    Args:
        id (str): id of package

    Raises:
        CtanPackageNotFoundError: If id not on CTAN or not downloadable

    Returns:
        dict: Dict containing json-response from CTAN
    """
    pkgInfo = requests.get(f"{_ctan_url}json/2.0/pkg/{id}").json()
    if "id" not in pkgInfo or "name" not in pkgInfo:
        raise CtanPackageNotFoundError("CTAN has no information about package with id " + id)
    
    if 'ctan' not in pkgInfo or not pkgInfo['ctan']:
        raise CtanPackageNotFoundError(f"{id} is on CTAN, but not downloadable")
    return pkgInfo

@cache
def get_version(id: str) -> Version:
    pkgInfo = get_package_info(id)
    if 'version' in pkgInfo:
        return Version(pkgInfo['version'])
    raise CtanPackageNotFoundError(f"{id} has no version on CTAN")


def download_pkg(dep: Dependency, pkgInfo: dict=None, url:str = None) -> DownloadedDependency:
    """Download package from CTAN, return DownloadedDependency containg details about download

    Args:
        dep (Dependency): Package to download
        pkgInfo (dict, optional): CTAN response from /packages for package
        url (str, optional): If present, use this url to download package from

    Returns:
        DownloadedDependency: Input dep with additional information
    """
    logger.debug(f"Downloading {dep.id} from CTAN")
    if not pkgInfo:
        pkgInfo = get_package_info(dep.id)
    
    if not url:
        url = _get_download_url(dep, pkgInfo)
    
    logger.info(f"CTAN: Installing {dep} from {url}")
    folder_path = download_and_extract_zip(url, dep)
    
    # Add version to dep so that installed version is written to lockfile
    if 'version' in pkgInfo:
        version = Version(pkgInfo['version'])
        dep.version = version
    else:
        logger.warn(f"CTAN: Couldn't find version for {dep}")
    
    try:
        ctan_path = pkgInfo['ctan']['path']
    except KeyError:
        ctan_path=None

    return DownloadedDependency(dep, folder_path, url, ctan_path=ctan_path)


def _get_download_url(dep, pkgInfo):
    # Extract download path
    if "install" in pkgInfo:
        path = pkgInfo['install']
        url = "https://mirrors.ctan.org/install" + path # Ends in .zip or similar
    
    elif "ctan" in pkgInfo:
        path = pkgInfo['ctan']['path']
        url = f"https://mirrors.ctan.org{path}.zip"
    else:
        if "id" in pkgInfo:
            raise CtanPackageNotFoundError(f"{pkgInfo['id']} cannot be downloaded from CTAN")
        raise CtanPackageNotFoundError(f"Couldn't find package {dep.id} on CTAN")
    
    return url