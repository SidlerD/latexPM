from src.API import CTAN
from src.models.Dependency import Dependency, DownloadedDependency

from src.helpers.DownloadHelpers import download_and_extract_zip
import logging
import urllib.parse
import requests
import os

_base_url = os.environ.get('VPTAN_HOST', "http://127.0.0.1") + ":" + os.environ.get('VPTAN_PORT', '8000')
logger = logging.getLogger("default")


def download_pkg(dep: Dependency, pkgInfo: dict = None, closest=False, url: str = None) -> DownloadedDependency:
    """Download package from VPTAN, return DownloadedDependency containg details about download

    Args:
        dep (Dependency): Package to download
        pkgInfo (dict, optional): CTAN response from /packages for package
        closest (bool, optional): If True and version not available on CTAN, \
            download the closest later version of the package
        url (str, optional): If present, use this url to download package from

    Returns:
        DownloadedDependency: Input dep with additional information
    """
    logger.info(f"Downloading {dep.id} from VPTAN")

    if not url:
        url = _get_url_for_version(dep, closest=closest)

    logger.info(f"VPTAN: Installing {dep} from {url}")
    folder_path = download_and_extract_zip(url, dep)

    if not pkgInfo:
        pkgInfo = CTAN.get_package_info(dep.id)
    try:
        ctan_path = pkgInfo['ctan']['path']
    except KeyError:
        ctan_path = None

    return DownloadedDependency(dep, folder_path, url, ctan_path=ctan_path)


def _get_url_for_version(dep: Dependency, closest: bool) -> str:
    v = dep.version

    url = f"{_base_url}/packages/{dep.id}"
    if v.date and v.number:
        url += f'?date={v.date}&number={v.number}'
    elif v.date:
        url += f'?date={v.date}'
    elif v.number:
        url += f'?number={v.number}'

    url += f'&closest={closest}' if '?' in url else f'?closest={closest}'

    logger.debug("VPTAN Download url: " + url)
    return url


def get_alias_of_package(id='', name='') -> dict:
    """Some packages are not available on CTAN directly, but are under another package, \
        where they are listed as 'aliases'
    Example: tikz is not available on CTAN as package, but is listed in alias field of pgf. \
        Therefore, we should download pgf to get tikz"""

    logger.debug(f'Searching for {id if id else name} in aliases')
    if not id and not name:
        raise ValueError("Please provide valid argument for at least one of id and name")

    params = {'id': id, 'name': name}
    url = _base_url + '/alias?' + urllib.parse.urlencode(params)

    response = requests.get(url)
    if not response.ok:
        raise ValueError(f"{id if id else name} has no alias")

    return response.json()
