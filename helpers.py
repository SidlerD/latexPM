import re
import os
import shutil
import zipfile
import requests
from Dependency import Dependency


#TODO: Packages can also be imported using \usepackage, account for that
#TODO: Seems like multiple packages can be imported using one RequirePackage, e.g.\RequirePackage{tikz,xcolor,fontspec} from hmtrump.sty
def extract_dependencies(dep: Dependency):
    print("Extracting dependencies of " + dep.name)

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
                deps_of_dep.add(Dependency(package_name, package_version, dep.path))

            # Extract dependencies of sty-file
            sty.seek(0) # Reset file position due to previous read
            cont = sty.readlines()
            matchLines = [line for line in cont if "RequirePackage" in line]

            pattern = r'\\RequirePackage\{(.*?)\}(?:\[(.*?)\])?'

            for input_string in matchLines:
                match = re.search(pattern, input_string)
                if match:
                    package_name = match.group(1)
                    package_version = match.group(2)
                    deps_of_files.add(Dependency(package_name, package_version))

    
    # Sort out deps whose files were included in the download of current dep
    # This assumes that when I download package A which depends on (included) fileB, fileB is included in the right version
    # Could check for assumption, but it seems versions in \RequirePackage are sometimes outdated and not up-to-date
    cleaned_deps_of_files = [d for d in deps_of_files if all([d.name != o.name for o in deps_of_dep])]

    print(f"Dependency {dep.name} included {len(deps_of_dep)} deps {deps_of_dep} as files and has {len(cleaned_deps_of_files)} {cleaned_deps_of_files} as dependencies")
    return list(deps_of_dep), cleaned_deps_of_files

def download_file(dep: Dependency): 
    """Returns path to folder where dep's files were downloaded"""
    print(f"Download {dep.name} {dep.version}")
    # Check if version on CTAN fits
    pkgInfo = requests.get("http://www.ctan.org/json/2.0/pkg/" + dep.name).json()
    if "version" not in pkgInfo:
        raise ValueError(f"Error: {dep.name} has no version on CTAN") #TODO: Remove
    
    ctan_version = pkgInfo["version"]
    if(not dep.version or ctan_version['date'] == dep.version or ctan_version['number'] == dep.version):
        folder_path = download_from_ctan(pkgInfo)
    else: # CTAN version outdated, need to download from TL-arch instead
        folder_path = download_from_TL(pkgInfo)

    return folder_path


def download_from_ctan(pkgInfo):
    # Extract download path
    if "install" in pkgInfo:
        path = pkgInfo['install']
        url = "https://mirror.ctan.org/install" + path # Should end in .zip or similar
        folder_path = download_and_extract_zip(url)

        return folder_path 
    
    if "ctan" in pkgInfo:
        path = pkgInfo['ctan']['path']
        url = f"https://mirror.ctan.org/tex-archive/{path}.zip"
        folder_path = download_and_extract_zip(url)

        return folder_path
    
    raise Exception(f"{pkgInfo.name} cannot be downloaded from CTAN")

def download_and_extract_zip(url):
    # Extract the filename from the URL
    file_name = url.split('/')[-1]
    
    # Download the ZIP file
    response = requests.get(url, allow_redirects=True)
    with open(file_name, 'wb') as file:
        file.write(response.content)
    
    # Extract the files into a folder
    folder_name = os.path.join("/packages", file_name.split('.')[0])  # Use the filename without the extension as the folder name
    os.makedirs(folder_name, exist_ok=True)
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(folder_name)
    
    # Return the path to the folder
    folder_path = os.path.abspath(folder_name)

    organize_files(folder_path)
    return folder_path


def organize_files(folder_path: str):
    """Ensure relevant files are at top-level of folder_path, unnecessary files/folders are deleted"""
    if(len(os.listdir(folder_path)) == 1): # Only one subfolder, move everything in it up
        sub_path = os.path.join(folder_path, os.listdir(folder_path)[0])
        for file_name in os.listdir(sub_path):
            source = os.path.join(sub_path, file_name)
            destination = os.path.join(os.path.dirname(sub_path), file_name)
            shutil.move(source, destination)

        # Remove the now empty subfolder
        os.rmdir(sub_path)


    if('tex' in os.listdir(folder_path)):
        # TODO: Get files at end of tex folder structure to top-level, delete other stuff
        pass

def download_from_TL(pkgInfo):
    raise NotImplementedError("Downloads from TL not supported yet")