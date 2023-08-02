import os
from os.path import basename, join, exists, abspath
import re
import logging
from src.API import CTAN, VPTAN
from src.exceptions.download.CTANPackageNotFound import CtanPackageNotFoundError
from src.models.Dependency import Dependency, DownloadedDependency


# prov_pkg_pattern = r'\\Provides(?:Package|File)\{(.*?)(?:\..*)?\}\[(.*?)\]'
"""Captures both ProvidesPackage and ProvidesFile. group1 = Pkg_name, group2 = version\n
    https://regex101.com/r/2iSv1O/1
"""

# FIXME: cls-files (I think also sty-files) can import package by using \input{file.sty} (I don't know which file types are supported for importing with \input)
req_pkg_pattern = r'^\s*(?<!%)\s*\\(?:RequirePackage|usepackage)\s*(?:\[(?:.*?)\])?\s*\{(.*?)\}\s*(?:\[(.*?)\])?.*'
"""Captures both RequiresPackage and usepackage. group1 = Pkg_name, group2 = version if available\n
    https://regex101.com/r/yKfVDC/1
"""
logger = logging.getLogger("default")

def extract_dependencies(dep: DownloadedDependency) -> list[Dependency]:
    logger.info("Extracting dependencies of " + dep.id)

    to_extract, already_extracted = [f'{dep.name}.sty'], []
    final_deps: list[Dependency] = []

    if not exists(join(dep.path, to_extract[0])):
        # No sty-file in package-files
        logger.info(f"{dep.id} does not include any .sty files. Dependency extraction skipped")
        return []

    sty_files = [file_name for file_name in dep.files if file_name.endswith('.sty')]
    file_names = [basename(sty_path).split('.')[0] for sty_path in sty_files]


    while to_extract:
        sty_name = to_extract.pop()
        if sty_name in already_extracted:
            continue

        already_extracted.append(sty_name)

        sty_path = join(dep.path, sty_name)

        if not os.path.exists(sty_path):
            if os.path.exists(os.path.abspath(sty_name)):
                sty_path = os.path.abspath(sty_name)
            else:
                raise RuntimeError(f"Cannot extract dependencies for {dep.id}: {sty_path} does not exist")
        
        with open(sty_path, "r") as sty:
            content = sty.read()
            matches: list[tuple] = re.findall(req_pkg_pattern, content, re.MULTILINE)
            for (package_names, package_version) in matches:
                package_names = package_names.split(',')
                for name in package_names:
                    # Why not check for ProvidesPackage here?: Latex imports by file name, not by ProvidesPackage. Test with pkgA.sty which \ProvidesPackage{pkgB}. Can only import with \usepackage{pkgA}
                    if name in file_names and name not in already_extracted and name not in to_extract: 
                        # ASSUMPTION: If file is included in download, it's included in right version. Therefore don't need to check version here
                        logger.debug(f"{sty_name} depends on {name}, which was included in its download")
                        to_extract.append(f'{name}.sty')
                    else:
                        try:
                            try:
                                pkg_id = CTAN.get_id_from_name(name)
                            except CtanPackageNotFoundError:
                                aliased_by = CTAN.get_alias_of_package(id=pkg_id)
                                pkg_id, name = aliased_by['id'], aliased_by['name']
                            
                            final_deps.append(Dependency(pkg_id, name, package_version))
                            logger.debug(f"Adding {name} as dependency of {dep.id}")
                        except CtanPackageNotFoundError as e:
                            logger.warning(f"{os.path.basename(sty_name)} from package {dep.id} depends on {name}, but CTAN has no information about {name}. {name} will not be installed. If problems arise, please install {name} manually.")

    logger.info(f"{dep} has {len(final_deps)} dependencies: {', '.join([dep.id for dep in final_deps])}")
    return list(final_deps)
    