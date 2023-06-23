import requests

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