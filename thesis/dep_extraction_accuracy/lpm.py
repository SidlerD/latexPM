from src.API import CTAN

from src.helpers.DependenciesHelpers import extract_dependencies
from src.models.Dependency import Dependency

def get_deps_of_pkgs(tlmgr_pkgs):
    res = []
    for pkg in tlmgr_pkgs:
        dep = Dependency(pkg['name'], pkg['name'])

        downloaded_dep = CTAN.download_pkg(dep)

        deps = extract_dependencies(downloaded_dep)
        res.append({
            'name': dep.name,
            'cat-date': str(downloaded_dep.version.date),
            'cat-version': downloaded_dep.version.number,
            'depends': [dep.name for dep in deps]
        })

    return res