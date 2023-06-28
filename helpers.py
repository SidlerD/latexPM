import os
import re
import shutil
import zipfile
import requests
from src.API import CTAN, TexLive
from src.models.Dependency import Dependency
from src.models.Version import Version


#TODO: Packages can also be imported using \usepackage, account for that
def extract_dependencies(dep: Dependency):
    # print("Extracting dependencies of " + dep.id)

    deps_of_files = set()
    deps_of_dep = set() # Files that were included in the download of dep

    sty_files = [os.path.join(dep.path, file_name) for file_name in os.listdir(dep.path) if file_name.endswith('.sty')] #TODO: .ins and .tex files
    
    for sty_path in sty_files:
        with open(sty_path, "r") as sty:
            # Add sty-file as dep
            pattern = r'\\ProvidesPackage\{(.*?)\}\[(.*?)\]'
            match = re.search(pattern, sty.read())
            if match:
                package_name = match.group(1)
                package_version = match.group(2)
                deps_of_dep.add(Dependency(CTAN.get_id_from_name(package_name), package_name, None, dep.path)) #TODO: Assumption that I dont document dependencies on included files, else I need to pass the version (not just none)

            # Extract dependencies of sty-file
            sty.seek(0) # Reset file position due to previous read
            cont = sty.readlines()
            matchLines = [line for line in cont if "RequirePackage" in line]

            pattern = r'\\RequirePackage\{(.*?)\}(?:\[(.*?)\])?'

            for input_string in matchLines:
                match = re.search(pattern, input_string)
                if match:
                    package_names = match.group(1).split(',')
                    package_version = match.group(2)
                    deps_of_files.update([Dependency(CTAN.get_id_from_name(name), name, package_version, dep.path) for name in package_names])

    
    # Sort out deps whose files were included in the download of current dep
    # This assumes that when I download package A which depends on (included) fileB, fileB is included in the right version
    # Could check for assumption, but it seems versions in \RequirePackage are sometimes outdated and not up-to-date
    cleaned_deps_of_files = [d for d in deps_of_files if all([d.id != o.id for o in deps_of_dep])]

    # print(f"Dependency {dep.id} included {len(deps_of_dep)} deps {deps_of_dep} as files and has {len(cleaned_deps_of_files)} {cleaned_deps_of_files} as dependencies")
    return list(deps_of_dep), cleaned_deps_of_files


def download_from_TL(pkgInfo):
    raise NotImplementedError("Downloads from TL not supported yet")