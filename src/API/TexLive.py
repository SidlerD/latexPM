from src.models.Dependency import Dependency, DownloadedDependency

from src.models.Version import Version
from src.helpers.DownloadHelpers import download_and_extract_zip
from src.exceptions.download.DownloadError import DownloadError
import logging

_base_url = "https://texlive.info/tlnet-archive/"
logger = logging.getLogger("default")

def download_pkg(dep: Dependency, pkgInfo=None) -> DownloadedDependency:
    logger.info(f"Downloading {dep.id} from CTAN")
    version = dep.version
    
    url = _get_url_for_version(version)

    logger.info(f"TL: Installing {dep} from {url}")
    folder_path = download_and_extract_zip(url, dep)
    
    return DownloadedDependency(dep, folder_path, url) 



def _get_url_for_version(version: Version):
    raise NotImplementedError("Download from TL not implemented yet")
    #TODO: Implement
    if(not version.date and not version.number):
        pass # return path to latest version on TL
    if(version.date):
        pass # Find closest entry after date, check compatibility, download

    
