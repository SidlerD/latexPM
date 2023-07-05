import os
import requests
import logging

from src.models.Dependency import Dependency, DownloadedDependency
from src.helpers.DownloadHelpers import download_and_extract_zip
from src.exceptions.download.CTANPackageNotFound import CtanPackageNotFoundError
from src.models.Version import Version

_ctan_url = "https://www.ctan.org/"
logger = logging.getLogger("default") # FIXME: Is this good??
    
def get_id_from_name(name: str) -> str:
    res = requests.get(f"{_ctan_url}search/json?phrase={name}").json()
    if "hits" not in res or res["hits"] == []:
        raise RuntimeError("CTAN has no information about package with name " + name)
    pkgInfo = requests.get(f"{_ctan_url}json/2.0{res['hits'][0]['path']}").json()
    
    return pkgInfo['id']

def get_name_from_id(id: str) -> str:
    res = requests.get(f"{_ctan_url}json/2.0/pkg/{id}").json()
    if "id" not in res:
        raise RuntimeError("CTAN has no information about package with id " + id)
    return res['name']

def get_package_info(id: str):
    pkgInfo = requests.get(f"{_ctan_url}json/2.0/pkg/{id}").json()
    if "id" not in pkgInfo or "name" not in pkgInfo:
        raise RuntimeError("CTAN has no information about package with id " + id)
    return pkgInfo

def get_version(id: str) -> Version:
    pkgInfo = get_package_info(id)
    if 'version' in pkgInfo:
        return Version(pkgInfo['version'])
    raise CtanPackageNotFoundError(f"{id} has no version on CTAN")

def download_pkg(dep: Dependency, pkgInfo=None, pkg_dir = "packages") -> DownloadedDependency:
    logger.info(f"Downloading {dep.id} from CTAN")
    if not pkgInfo:
        pkgInfo = get_package_info(dep.id)
        
    # Extract download path
    if "install" in pkgInfo:
        path = pkgInfo['install']
        url = "https://mirror.ctan.org/install" + path # Should end in .zip or similar
    
    elif "ctan" in pkgInfo:
        path = pkgInfo['ctan']['path']
        url = f"https://mirror.ctan.org/tex-archive/{path}.zip"
    else:
        if "id" in pkgInfo:
            raise CtanPackageNotFoundError(f"{pkgInfo['id']} cannot be downloaded from CTAN")
        raise CtanPackageNotFoundError(f"Couldn't find package {dep.id} on CTAN")
    
    logger.info(f"CTAN: Installing {dep} from {url}")
    folder_path = download_and_extract_zip(url, pkg_dir)

    return DownloadedDependency(dep, folder_path, url)