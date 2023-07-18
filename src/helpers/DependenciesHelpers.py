import os
import re
import logging
from src.API import CTAN, TexLive
from src.exceptions.download.CTANPackageNotFound import CtanPackageNotFoundError
from src.models.Dependency import Dependency, DownloadedDependency


prov_pkg_pattern = r'\\Provides(?:Package|File)\{(.*?)(?:\..*)?\}\[(.*?)\]'
"""Captures both ProvidesPackage and ProvidesFile. group1 = Pkg_name, group2 = version\n
    https://regex101.com/r/2iSv1O/1
"""

# ASSUMPTION: usepackage{} is always first command on line, doesn't match it if there's anything else than spaces before use/requirepackage
req_pkg_pattern = r'^\s*(?<!%)\s*\\(?:RequirePackage|usepackage)(?:\[(?:.*?)\])?\{(.*?)\}(?:\[(.*?)\])?.*'
"""Captures both RequiresPackage and usepackage. group1 = Pkg_name, group2 = version if available\n
    https://regex101.com/r/BnKbkR/1
"""

def extract_dependencies(dep: DownloadedDependency) -> list[Dependency]:
    logger = logging.getLogger("default")
    logger.info("Extracting dependencies of " + dep.id)

    deps_of_files = set()
    included_deps = [] # Files that were included in the download of dep

    sty_files = [os.path.join(dep.path, file_name) for file_name in dep.files if file_name.endswith('.sty')] #TODO: .ins and .tex files
    
    # Get names of "packages" included in download
    for sty_path in sty_files:
        with open(sty_path, "r") as sty:
            # Dependencies that are already included when downloading package
            match = re.search(prov_pkg_pattern, sty.read())
            if match: # Get name from command in sty-file
                package_name = match.group(1)
                package_version = match.group(2)
                included_deps.append(package_name) # Assumption that I dont document dependencies on included files, else I need to pass the version (not just none)
            else: # Take file-name as package-name
                package_name = os.path.basename(sty_path).split('.')[0]
                if(package_name):
                    included_deps.append(package_name)
                    logger.debug(f"""File {os.path.basename(sty_path)} doesn't have a ProvidesPackage or ProvidesFile. Had to fallback and use its filename. This could lead to problems""") #TODO: Make this warning, not debug
    # Get dependencies of files
    for sty_path in sty_files:
        with open(sty_path, "r") as sty:
            matches: list[tuple] = re.findall(req_pkg_pattern, sty.read())
            for (package_names, package_version) in matches:
                package_names = package_names.split(',')
                for name in package_names:
                    if name in included_deps:
                        # Sort out deps whose files were included in the download of current dep
                        # This assumes that when I download package A which depends on (included) fileB, fileB is included in the right version
                        # Could check for assumption, but it seems versions in \RequirePackage are sometimes outdated and not up-to-date
                        logger.debug(f"{dep.id} depends on {name}, which was included in its download")
                        continue
                    try:
                        deps_of_files.add(Dependency(CTAN.get_id_from_name(name), name, package_version))
                        logger.debug(f"Adding {name} as dependency of {dep.id}")
                    except CtanPackageNotFoundError as e:
                        logger.warning(f"{os.path.basename(sty_path)} from package {dep.id} depends on {name}, but CTAN has no information about {name}. {name} will not be installed. If problems arise, please install {name} manually.")

    logger.info(f"{dep} has {len(deps_of_files)} dependencies: {', '.join([dep.id for dep in deps_of_files])}")
    return list(deps_of_files)