import requests
from src.models.Dependency import Dependency

from src.models.Version import Version

_base_url = "https://texlive.info/tlnet-archive/"

def download_pkg(dep: Dependency, pkgInfo=None, pkg_dir="packages"):
    version = dep.version
    
    path = _get_path_for_version(version)

    print(f"TL: Installing {dep} from {path}")



def _get_path_for_version(version: Version):
    if(not version.date and not version.number):
        pass # return path to latest version on TL
    if(version.date):
        pass # Find closest entry after date, check compatibility, download

    
