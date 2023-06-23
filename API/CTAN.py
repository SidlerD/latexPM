import requests

from helpers import download_and_extract_zip

_ctan_url = "https://www.ctan.org/"
    
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

def download_pkg(pkgInfo, pkg_dir):
    # Extract download path
    if "install" in pkgInfo:
        path = pkgInfo['install']
        url = "https://mirror.ctan.org/install" + path # Should end in .zip or similar
    
    elif "ctan" in pkgInfo:
        path = pkgInfo['ctan']['path']
        url = f"https://mirror.ctan.org/tex-archive/{path}.zip"
    else:
        raise Exception(f"{pkgInfo['id']} cannot be downloaded from CTAN")

    folder_path = download_and_extract_zip(url, pkg_dir)

    return folder_path