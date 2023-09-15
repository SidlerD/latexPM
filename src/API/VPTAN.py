from src.models.Dependency import Dependency, DownloadedDependency

from src.helpers.DownloadHelpers import download_and_extract_zip
import logging
import urllib.parse
import requests

_base_url = "http://localhost:8000"
logger = logging.getLogger("default")


def download_pkg(dep: Dependency, pkgInfo=None, closest=False) -> DownloadedDependency:
    logger.info(f"Downloading {dep.id} from VPTAN")

    url = _get_url_for_version(dep, closest=closest)

    logger.info(f"VPTAN: Installing {dep} from {url}")
    folder_path = download_and_extract_zip(url, dep)

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
    """Some packages are not available on CTAN directly, but are under another package, where they are listed as 'aliases'
    Example: tikz is not available on CTAN as package, but is listed in alias field of pgf. Therefore, we should download pgf to get tikz"""
    logger.debug(f'Searching for {id if id else name} in aliases')
    if not id and not name:
        raise ValueError("Please provide valid argument for at least one of id and name")

    params = {'id': id, 'name': name}
    url = _base_url + '/alias?' + urllib.parse.urlencode(params)

    response = requests.get(url)
    if not response.ok:
        raise ValueError(f"{id if id else name} has no alias")  # TODO: Raise something more specific here

    return response.json()
