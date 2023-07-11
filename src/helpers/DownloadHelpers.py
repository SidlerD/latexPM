import os
from os.path import join, isdir
import shutil
import zipfile
import requests
import logging
from src.core import config

logger = logging.getLogger("default")

def download_and_extract_zip(url):
    # Extract the filename from the URL
    pkg_folder = os.path.abspath(config.get_package_dir())
    logger.debug(f"Downloading files into {pkg_folder}")
    zip_file_name = os.path.join(pkg_folder, url.split('/')[-1]) 
    
    # Ensure that package folder exists
    if not os.path.exists(pkg_folder):
        os.mkdir(pkg_folder)

    # Download the ZIP file
    response = requests.get(url, allow_redirects=True)
    with open(zip_file_name, 'wb') as file:
        file.write(response.content)
    
    # Extract the files into a folder
    # folder_name = zip_file_name.split('.')[0]  # Use the filename without the extension as the folder name
    folder_name = pkg_folder
    os.makedirs(folder_name, exist_ok=True)
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall(folder_name)
    
    # Return the path to the folder
    folder_path = os.path.abspath(folder_name)

    os.remove(zip_file_name)
    organize_files(folder_path)

    return folder_path


def organize_files(folder_path: str):
    """Ensure relevant files are at top-level of folder_path, unnecessary files/folders are deleted, convert .ins to .sty"""
    
    if not os.path.exists(folder_path):
        raise OSError(f"Error while cleaning up download folder: {folder_path} is not a valid path")
    
    # Get path for each relevant file
    relevant_files = []
    for root, dirs, files in os.walk(folder_path):
        relevant_files.extend([os.path.join(root, file) for file in files if file.endswith(('.ins', '.sty', '.tex'))]) #TODO: Is .tex relevant?
    # Move relevant files to cwd
    for file in relevant_files:
        destination = os.path.join(folder_path, os.path.basename(file))
        shutil.move(file, destination) 
    # Remove the folders
    #TODO: Does not work yet: Remove folders in cwd recursively, leave files at cwd
    folders = []
    for f in os.listdir(folder_path):
        path = join(folder_path, f)
        if isdir(path):
            folders.append(path)

    for folder in folders:
        shutil.rmtree(folder)