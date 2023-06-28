from src.models.Dependency import Dependency

from src.models.Version import Version
from src.helpers.DownloadHelpers import download_and_extract_zip

_base_url = "https://texlive.info/tlnet-archive/"

def download_pkg(dep: Dependency, pkgInfo=None, pkg_dir="packages") -> str:
    version = dep.version
    
    url = _get_url_for_version(version)

    print(f"TL: Installing {dep} from {url}")
    folder_path = download_and_extract_zip(url, pkg_dir)
    
    return folder_path 



def _get_url_for_version(version: Version):
    #TODO: Implement
    if(not version.date and not version.number):
        pass # return path to latest version on TL
    if(version.date):
        pass # Find closest entry after date, check compatibility, download

    
