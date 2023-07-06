import os
import re
import shutil
import zipfile
import requests
import logging
from src.API import CTAN, TexLive
from src.models.Dependency import Dependency, DownloadedDependency
from src.models.Version import Version

prov_pkg_pattern = r'\\Provides(?:Package|File)\{(.*?)(?:\..*)?\}\[(.*?)\]'
"""Captures both ProvidesPackage and ProvidesFile. group1 = Pkg_name, group2 = version\n
    https://regex101.com/r/2iSv1O/1
"""

req_pkg_pattern = r'\\(?:RequirePackage|usepackage)(?:\[(?:.*?)\])?\{(.*?)\}(?:\[(.*?)\])?'
"""Captures both RequiresPackage and usepackage. group1 = Pkg_name, group2 = version if available\n
    https://regex101.com/r/DZFYZH/1
"""

def extract_dependencies(dep: DownloadedDependency) -> list[Dependency]:
    logger = logging.getLogger("default")
    logger.info("Extracting dependencies of " + dep.id)

    deps_of_files = set()
    included_deps = [] # Files that were included in the download of dep

    sty_files = [os.path.join(dep.path, file_name) for file_name in os.listdir(dep.path) if file_name.endswith('.sty')] #TODO: .ins and .tex files
    
    # Get names of "packages" included in download
    for sty_path in sty_files:
        with open(sty_path, "r") as sty:
            # Dependencies that are already included when downloading package
            match = re.search(prov_pkg_pattern, sty.read())
            if match:
                package_name = match.group(1)
                package_version = match.group(2)
                included_deps.append(package_name) #TODO: Assumption that I dont document dependencies on included files, else I need to pass the version (not just none)
            else:
                logger.warning(f"""File {os.path.basename(sty_path)} doesn't have a ProvidesPackage or ProvidesFile. 
                               This means that if any of {dep.id}'s files depend on it, 
                               it will be downloaded separately, which could lead to Errors.""")
                # TODO: Could get name from file name
    # Get dependencies of files
    for sty_path in sty_files:
        with open(sty_path, "r") as sty:
            cont = sty.readlines()
            matchLines = [line for line in cont if "RequirePackage" in line]

            for input_string in matchLines:
                match = re.search(req_pkg_pattern, input_string)
                if match:
                    package_names = match.group(1).split(',')
                    package_version = match.group(2)
                    for name in package_names:
                        if name in included_deps:
                            # Sort out deps whose files were included in the download of current dep
                            # This assumes that when I download package A which depends on (included) fileB, fileB is included in the right version
                            # Could check for assumption, but it seems versions in \RequirePackage are sometimes outdated and not up-to-date
                            logger.debug(f"{dep.id} depends on {name}, which was included in its download")
                            continue
                        logger.debug(f"Adding {name} as dependency of {dep.id}")
                        deps_of_files.add(Dependency(CTAN.get_id_from_name(name), name, package_version))

    logger.debug(f"{dep} has {len(deps_of_files)} dependencies")
    return list(deps_of_files)