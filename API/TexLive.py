import requests
from Dependency import Dependency

from Version import Version

base_url = "https://texlive.info/tlnet-archive/"

def download_pkg(dep: Dependency, pkg_dir):
    version = dep.version
    
    path = get_path_for_version(version)


def get_path_for_version(version: Version):
    if(not version.date and not version.number):
        pass # Download latest version
    if(version.date):
        pass # Find closest entry after date, check compatibility, download

    
