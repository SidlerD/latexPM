import os
from os.path import join, isdir, isfile, abspath, basename, exists
import shutil
import subprocess
import zipfile
import requests
import logging
from src.API import CTAN
from src.core import config
from src.exceptions.download.DownloadError import DownloadError, VersionNotAvailableError
from src.models.Dependency import Dependency

logger = logging.getLogger("default")

def download_and_extract_zip(url: str, dep: Dependency) -> str:
    # Extract the filename from the URL
    pkg_folder = abspath(config.get_package_dir())
    try:
        pkgInfo = CTAN.get_package_info(dep.id)
        ctan_path = pkgInfo['ctan']['path']
        download_folder = join(pkg_folder, ctan_path.split('/')[-1])
    except KeyError:
        logger.debug(f"Using {dep.name} as fallback for folder name")
        download_folder = join(pkg_folder, dep.name)

    zip_file_name =  join(download_folder, basename(download_folder) + '.zip') 

    # Download the ZIP file
    response = requests.get(url, allow_redirects=True)
    if not response.ok:
        raise VersionNotAvailableError(response.text if hasattr(response, 'text') and response.text else f'Cannot download {dep}: {response.reason}')
    
    os.makedirs(download_folder, exist_ok=True)
    logger.debug(f"Downloading files into {download_folder}")
    
    with open(zip_file_name, 'wb') as file:
        file.write(response.content)
    
    # Extract the files into a folder
    # This sometimes fails, but in those cases opening .zip with Windows doesn't work either. Seems like some downloads return faulty zips
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall(download_folder)

    # Return the path to the folder
    os.remove(zip_file_name)
    organize_files(download_folder, tds=url.endswith('.tds.zip'))

    return download_folder


def organize_files(folder_path: str, tds: bool):
    """Ensure relevant files are at top-level of folder_path, unnecessary files/folders are deleted, convert .ins/.dtx to .sty"""
    
    if not exists(folder_path):
        raise OSError(f"Error while cleaning up download folder: {folder_path} is not a valid path")
    
    files_path = folder_path
    if tds:
        # TDS-packaged packages (TEX Directory Standard) follow a certain folder structure: 
        #   the subfolder 'tex' contains the built files that latex uses, other folders contain the source code and documentation 
        # For more information, see https://ctan.org/TDS-guidelines

        # If a package is tds-packaged, we only need the files in subfolder 'tex' and don't need to try and build the source files
        if exists(join(folder_path, 'tex')):
            # Inspect files in files_path, but move them to folder_path and delete subfolders of folder_path
            files_path = join(folder_path, 'tex')
            

    # Get path for all files in subdirs
    relevant_files = []
    for root, dirs, files in os.walk(files_path):
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

    if tds:
        return
    
    # Convert .ins and .dtx to .sty and .cls
    old_cwd = os.getcwd()
    os.chdir(folder_path)

    ins_files = [abspath(file) for file in os.listdir() if isfile(abspath(file)) and file.endswith('.ins')]
    dtx_files = [abspath(file) for file in os.listdir() if isfile(abspath(file)) and file.endswith('.dtx')]

    if len(ins_files) > 0:
        for ins_file in ins_files: # Should normally only be 1 ins-file i think
            name = (basename(ins_file)).split('.')[0]
            logger.debug(f"Creating sty-files from {basename(ins_file)}")

            # May overwrite existing .sty files, but cant check for that since they could have different names than the .dtx they were built from
            try:
                # DECIDE: Could parse sty-file names that are generated from ins-file and delete them, so that prompt does not occur
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
    
    # TODO: Remove files I know are unnecessary (e.g. pdf, log, aux)

    os.chdir(old_cwd)