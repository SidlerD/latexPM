import json
import os
import shutil
import tempfile

from src.API import CTAN
from src.helpers.DependenciesHelpers import extract_dependencies
from src.models.Dependency import Dependency

file_name = 'lpm_deps_of_files_output.json'


def get_deps_of_pkgs(tlmgr_pkgs):
    res = []
    old_cwd = os.getcwd()
    tmpdir = tempfile.mkdtemp()
    os.chdir(tmpdir)

    for pkg in tlmgr_pkgs:
        try:
            dep = Dependency(pkg['name'], pkg['name'])

            downloaded_dep = CTAN.download_pkg(dep)

            deps = extract_dependencies(downloaded_dep)
            res.append({
                'name': dep.name,
                'cat-date': str(downloaded_dep.version.date),
                'cat-version': downloaded_dep.version.number,
                'depends': [dep.name for dep in deps]
            })
        except Exception as e:
            print(e)

    os.chdir(old_cwd)
    shutil.rmtree(tmpdir)

    with open(file_name, 'w') as f:
        json.dump(res, f, indent=2)

    return res
