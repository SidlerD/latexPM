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
    # FIXME: This sometimes fails, but in those cases opening .zip with Windows doesn't work either. Seems like some downloads return faulty zips
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall(download_folder)
    
    # Return the path to the folder
    os.remove(zip_file_name)
    organize_files(download_folder)

    return download_folder


def organize_files(folder_path: str):
    """Ensure relevant files are at top-level of folder_path, unnecessary files/folders are deleted, convert .ins/.dtx to .sty"""
    
    if not exists(folder_path):
        raise OSError(f"Error while cleaning up download folder: {folder_path} is not a valid path")
    
    # Get path for all files in subdirs
    relevant_files = []
    for root, dirs, files in os.walk(folder_path):
        relevant_files.extend([join(root, file) for file in files])
    # Move files to top of folder
    for ins_file in relevant_files:
        destination = os.path.join(folder_path, os.path.basename(ins_file))
        shutil.move(ins_file, destination) 
    # Remove the folders
    folders = []
    for f in os.listdir(folder_path):
        path = join(folder_path, f)
        if isdir(path):
            folders.append(path)
    for folder in folders:
        shutil.rmtree(folder)

    # Convert .ins and .dtx to .sty
    old_cwd = os.getcwd()
    os.chdir(folder_path)

    ins_files = [abspath(file) for file in os.listdir() if isfile(abspath(file)) and file.endswith('.ins')]
    dtx_files = [abspath(file) for file in os.listdir() if isfile(abspath(file)) and file.endswith('.dtx')]

    if len(ins_files) > 0:
        for ins_file in ins_files: # Should normally only be 1 ins-file i think
            name = (basename(ins_file)).split('.')[0]
            logger.debug(f"Creating sty-files from {basename(ins_file)}")

            # May overwrite existing .sty files, but cant check for that since they could have different names than the .dtx they were built from
            # DECIDE: Could parse sty-file names that are generated from ins-file, if exists delete it and regenerate (cant just not do latex ins-file, since that might also generate other files)
            try:
                # FIXME: In case of sty-file already existing, enter 'n' instead of waiting for timeout. Problem: THere's also cases where prompt is for something else, where I do not want to say 'n'
                subprocess.run(['latex', ins_file], stdout=subprocess.DEVNULL, timeout=3)
            except Exception as e:
                # Possible reasons for timeout: File should not be executed, .sty file already exists and user gets prompted wheter or not to overwrite
                logger.warning(f"Problem while installing {name}.ins: {e}")
    else:     
        for dtx_file in dtx_files:
            name = (basename(dtx_file)).split('.')[0]
            try:
                logger.debug(f"Trying to create sty file from {name}.dtx because no .ins found")
                subprocess.run(['tex', dtx_file], stdout=subprocess.DEVNULL, timeout=2)
            except Exception as e:
                logger.warning(f"Problem while trying to generate sty-files from {name}.dtx: {e}")
    
    # TODO: Remove all files except .sty

    os.chdir(old_cwd)