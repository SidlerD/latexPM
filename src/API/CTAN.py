import json
from os.path import isfile, abspath
import requests
import logging
from functools import cache

from src.models.Dependency import Dependency, DownloadedDependency
from src.helpers.DownloadHelpers import download_and_extract_zip
from src.exceptions.download.CTANPackageNotFound import CtanPackageNotFoundError
from src.models.Version import Version

_ctan_url = "https://www.ctan.org/"
logger = logging.getLogger("default") # DECIDE: Is this good??

@cache
def get_id_from_name(name: str) -> str:
    all = requests.get(f"{_ctan_url}json/2.0/packages").json()
    for pkg in all:
        if pkg['name'] == name:
            return pkg['key']
    raise CtanPackageNotFoundError(f"CTAN has no information about package with name {name}")

@cache
def get_name_from_id(id: str) -> str:
    res = get_package_info(id)
    if "id" in res:
        return res['name']
    raise CtanPackageNotFoundError("CTAN has no information about package with id " + id)

@cache
def get_package_info(id: str):
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


def download_pkg(dep: Dependency, pkgInfo=None, url:str = None) -> DownloadedDependency:
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
        url = "https://mirror.ctan.org/install" + path # Should end in .zip or similar
    
    elif "ctan" in pkgInfo:
        path = pkgInfo['ctan']['path']
        url = f"https://mirror.ctan.org{path}.zip"
    else:
        if "id" in pkgInfo:
            raise CtanPackageNotFoundError(f"{pkgInfo['id']} cannot be downloaded from CTAN")
        raise CtanPackageNotFoundError(f"Couldn't find package {dep.id} on CTAN")
    
    return url