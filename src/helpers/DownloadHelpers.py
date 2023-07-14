import os
from os.path import join, isdir, isfile, abspath, basename, exists
import shutil
import subprocess
import zipfile
import requests
import logging
from src.core import config
from src.models.Dependency import Dependency

logger = logging.getLogger("default")

def download_and_extract_zip(url: str, dep: Dependency):
    # Extract the filename from the URL
    pkg_folder = abspath(config.get_package_dir())
    download_folder = join(pkg_folder, dep.name)
    zip_file_name =  join(download_folder, url.split('/')[-1]) 

    logger.debug(f"Downloading files into {download_folder}")

    os.makedirs(download_folder, exist_ok=True)
    
    # Download the ZIP file
    response = requests.get(url, allow_redirects=True)
    with open(zip_file_name, 'wb') as file:
        file.write(response.content)
    
    # Extract the files into a folder
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall(download_folder)
    
    # Return the path to the folder
    os.remove(zip_file_name)
    organize_files(download_folder)

    return download_folder


def organize_files(folder_path: str):
    """Ensure relevant files are at top-level of folder_path, unnecessary files/folders are deleted, convert .ins to .sty"""
    
    if not exists(folder_path):
        raise OSError(f"Error while cleaning up download folder: {folder_path} is not a valid path")
    
    # Get path for each relevant file
    relevant_files = []
    for root, dirs, files in os.walk(folder_path):
        relevant_files.extend([join(root, file) for file in files if file.endswith(('.ins', '.sty', '.tex', '.dtx'))]) #DECIDE: Is .tex relevant?
    
    # Move relevant files to top of folder
    for file in relevant_files:
        destination = os.path.join(folder_path, os.path.basename(file))
        shutil.move(file, destination) 
    
    # Remove the folders
    folders = []
    for f in os.listdir(folder_path):
        path = join(folder_path, f)
        if isdir(path):
            folders.append(path)
    for folder in folders:
        shutil.rmtree(folder)

    # Convert .ins to .sty
    old_cwd = os.getcwd()
    os.chdir(folder_path)

    for file in os.listdir():
        if isfile(abspath(file)) and file.endswith(('.ins', '.dtx')):
            name = file.split('.')[0]
            logger.debug(f"Creating {name}.sty file")
            # Check that .ins and .tex files exist (Needed to generate .sty)
            if exists(name + '.ins') and exists(name + '.dtx'):
                try:
                    if not exists(abspath(name + '.sty')): # If sty doesn't exist, create it
                        subprocess.run(['latex', f"{name}.ins"], stdout=subprocess.DEVNULL)
                    os.remove(f"{name}.ins")
                    os.remove(f"{name}.dtx")
                    if exists(f"{name}.log"):
                        os.remove(f"{name}.log")
                    if exists(f"{name}.aux"):
                        os.remove(f"{name}.aux")
                except Exception as e:
                    logger.warning(f"Problem while trying to generate {name}.sty: {e}")
            else:
                logger.info(f"Tried creating {name}.sty, but not all needed files present: Need {name}.ins and {name}.dtx")
            

    os.chdir(old_cwd)