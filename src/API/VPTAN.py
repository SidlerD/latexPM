from src.models.Dependency import Dependency, DownloadedDependency

from src.models.Version import Version
from src.helpers.DownloadHelpers import download_and_extract_zip
from src.exceptions.download.DownloadError import DownloadError
import logging

_base_url = "http://127.0.0.1:8000/packages"
logger = logging.getLogger("default")

def download_pkg(dep: Dependency, pkgInfo=None) -> DownloadedDependency:
    logger.info(f"Downloading {dep.id} from VPTAN")
    
    url = _get_url_for_version(dep)

    logger.info(f"VPTAN: Installing {dep} from {url}")
    folder_path = download_and_extract_zip(url, dep)
    
    return DownloadedDependency(dep, folder_path, url) 



def _get_url_for_version(dep: Dependency) -> str:
    v = dep.version

    url = f"{_base_url}/{dep.id}"
    if v.date and v.number:
        url += f'?date={v.date}&number={v.number}'
    elif v.date:
        url += f'?date={v.date}'
    elif v.number:
        url += f'?number={v.number}'

    logger.debug("VPTAN Download url: " + url)
    return url