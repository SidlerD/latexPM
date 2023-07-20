import json
from os.path import isfile, abspath
import requests
import logging
from functools import cache

from src.models.Dependency import Dependency, DownloadedDependency
from src.helpers.DownloadHelpers import download_and_extract_zip
from src.exceptions.download.CTANPackageNotFound import CtanPackageNotFoundError
from src.models.Version import Version

_ctan_url = "https://www.ctan.org/"
logger = logging.getLogger("default") # DECIDE: Is this good??
aliases_file = 'CTAN_aliases.json'
    
@cache
def get_id_from_name(name: str) -> str:
    all = requests.get(f"{_ctan_url}json/2.0/packages").json()
    for pkg in all:
        if pkg['name'] == name:
            return pkg['key']
    raise CtanPackageNotFoundError(f"CTAN has no information about package with name {name}")

@cache
def get_name_from_id(id: str) -> str:
    res = requests.get(f"{_ctan_url}json/2.0/pkg/{id}").json()
    if "id" in res:
        return res['name']
    raise CtanPackageNotFoundError("CTAN has no information about package with id " + id)

def get_alias_of_package(id = '', name = '') -> dict:
    """Some packages are not available on CTAN directly, but are under another package, where they are listed as 'aliases'
    Example: tikz is not available on CTAN as package, but is listed in alias field of pgf. Therefore, we should download pgf to get tikz"""
    logger.debug(f'Searching for {id if id else name} in aliases')
    if not id and not name:
        raise ValueError(f"Please provide valid argument for at least one of id and name")
    
    def find():
        if not isfile(abspath(aliases_file)):
            update_aliases()
        with open(aliases_file, "r") as f:
            aliases = json.load(f)
            for alias in aliases:
                if id and alias['id'] == id:
                    return alias['aliased_by']
                elif name and alias['name'] == name:
                    return alias['aliased_by']
    res = find()
    if res:
        logger.debug(f"{id if id else name} is aliased by {res}")
        return res
    
    logger.debug(f"Couldn't find {id if id else name} in list of aliases")
    update_aliases()

    res = find()
    if res:
        logger.debug(f"{id if id else name} is aliased by {res}")
        return res
            
    raise CtanPackageNotFoundError(f"{id if id else name} is not available on CTAN under any alias")

def update_aliases():
    # TODO: Should let user choose whether to do this
    logger.info('Updating list of aliases from CTAN. Please note that this can take very long')
    all = requests.get(f"{_ctan_url}json/2.0/packages").json()
    aliases = []
    for pkg in all:
        try:
            pkgInfo = get_package_info(pkg['key'])
            if 'aliases' in pkgInfo and pkgInfo['aliases']:
                try:
                    alias_info = pkgInfo['aliases']
                    for alias in alias_info:
                        aliases.append({'name': alias['name'], 'id': alias['id'], 'aliased_by': {'id': pkg['key'], 'name': pkg['name']}})
                except Exception as e:
                    logger.warning(f'Something went wrong while extracting alias for {pkgInfo["id"]}, alias = {pkgInfo["aliases"]}')
                    logging.warning(e)
        except CtanPackageNotFoundError as e:
            logging.warning(e)
    
    with open(aliases_file, 'w') as f:
        json.dump(f, aliases, indent=2)

@cache
def get_package_info(id: str):
    pkgInfo = requests.get(f"{_ctan_url}json/2.0/pkg/{id}").json()
    if "id" not in pkgInfo or "name" not in pkgInfo:
        raise CtanPackageNotFoundError("CTAN has no information about package with id " + id)
    return pkgInfo

@cache
def get_version(id: str) -> Version:
    pkgInfo = get_package_info(id)
    if 'version' in pkgInfo:
        return Version(pkgInfo['version'])
    raise CtanPackageNotFoundError(f"{id} has no version on CTAN")

def download_pkg(dep: Dependency, pkgInfo=None) -> DownloadedDependency:
    logger.debug(f"Downloading {dep.id} from CTAN")
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
    folder_path = download_and_extract_zip(url, dep)

    return DownloadedDependency(dep, folder_path, url)