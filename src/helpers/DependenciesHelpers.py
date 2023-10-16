import logging
import os
import re
from os.path import basename, join

from src.API import CTAN, VPTAN
from src.exceptions.download.CTANPackageNotFound import \
    CtanPackageNotFoundError
from src.models.Dependency import Dependency, DownloadedDependency

# FIXME: cls-files (I think also sty-files) can import package by using \input{file.sty} \
# (I don't know which file types are supported for importing with \input)
req_pkg_pattern = r'^\s*\\(?:RequirePackage|usepackage)\s*?(?:\[(?:[\s\S]*?)\])?\s*?\{(.*?)\}\s*?(?:\[(.*?)\])?.*?$'
"""Captures both RequiresPackage and usepackage. group1 = Pkg_name, group2 = version if available\n
    https://regex101.com/r/gFxWPO/3 (Regex in link may be out of date)
"""
logger = logging.getLogger("default")


def extract_dependencies(dep: DownloadedDependency) -> list[Dependency]:
    """Extract all dependencies from all files of provided package

    Args:
        dep (DownloadedDependency): Package to extract dependencies from

    Raises:
        RuntimeError: One of the files of package cannot be found

    Returns:
        list[Dependency]: List of all dependencies of package that were not included in the packages download
    """
    logger.info("Extracting dependencies of " + dep.id)

    # TODO: Check whether extracting from .def files is a good idea
    #       Reason for including .def for extraction: when using tikz,
    #       epstopdf-base is required by graphics-def/pdftex.def

    # Names of files to extract dependencies from
    to_extract = [elem for elem in os.listdir(dep.path) if elem.endswith(('.sty', '.def', '.cls'))]
    # File-names from to_extract, but without file extension
    included_file_names = [basename(sty_path).split('.')[0] for sty_path in to_extract]

    already_extracted = []
    final_deps: list[Dependency] = []

    # For file in download
    while to_extract:
        sty_name = to_extract.pop()
        if sty_name in already_extracted:
            continue

        already_extracted.append(sty_name)

        sty_path = join(dep.path, sty_name)

        # Check if file exists
        if not os.path.exists(sty_path):
            if os.path.exists(os.path.abspath(sty_name)):
                sty_path = os.path.abspath(sty_name)
            else:
                raise RuntimeError(f"Cannot extract dependencies for {dep.id}: {sty_path} does not exist")

        with open(sty_path, "r", errors='ignore') as sty:
            # Match all import-commands
            content = sty.read()
            matches: list[tuple[str, str]] = re.findall(req_pkg_pattern, content, re.MULTILINE)
            # For each import command
            for (package_names, package_version) in matches:
                package_names = package_names.split(',')
                # For each style-file which that import command imports
                for name in package_names:
                    name = name.strip()
                    # If style-file included in package's files, continue to next
                    if name in included_file_names:
                        # ASSUMPTION: If file is included in download, it's included in right version.
                        #             Therefore don't need to check version here
                        logger.debug(f"{sty_name} depends on {name}, which was included in its download")
                    # If dependency already in list of dependencies
                    elif name in [dep.name for dep in final_deps]:
                        continue
                    else:
                        try:
                            # Build Dependency-object for dependency
                            try:
                                pkg_id = CTAN.get_id_from_name(name)
                                new_dep = Dependency(pkg_id, name, package_version)
                            except CtanPackageNotFoundError:
                                logger.info(f"Cannot find {name}. Searching in aliases...")
                                alias = VPTAN.get_alias_of_package(id=name, name=name)
                                alias_id, alias_name = alias['id'], alias['name']
                                pkg_id, name = alias['aliased_by']['id'], alias['aliased_by']['name']
                                new_dep = Dependency(pkg_id, name, package_version,
                                                     alias={'id': alias_id, 'name': alias_name})

                            # Add dependency to list of dependencies
                            final_deps.append(new_dep)
                            logger.debug(f"Adding {name} as dependency of {dep.id}")

                        # Package is not on CTAN and has no alias
                        except ValueError:
                            logger.warning(f"{os.path.basename(sty_name)} from package {dep.id} depends on {name}, \
                                but CTAN has no information about {name}. {name} will not be installed. \
                                If problems arise, please install {name} manually.")

    logger.info(f"{dep} has {len(final_deps)} dependencies: {', '.join([dep.id for dep in final_deps])}")
    return final_deps
