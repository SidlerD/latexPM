import os
from os.path import join, isdir, isfile, abspath, basename, exists
import shutil
import subprocess
import zipfile
import requests
import logging
from src.API import CTAN
from src.exceptions.download.DownloadError import DownloadError
from src.models.Dependency import Dependency

logger = logging.getLogger("default")


def download_and_extract_zip(url: str, dep: Dependency) -> str:
    """Download and extract a zip-file, organize files using DownloadHelpers.organize_files

    Args:
        url (str): Url to download zip-file from
        dep (Dependency): Package that is in zip-file

    Raises:
        DownloadError: If url responds with status-code above 400

    Returns:
        str: Path to folder that now contains the package files
    """
    # Extract the filename from the URL
    pkg_folder = abspath('packages')

    # Figure out name to use for package
    try:
        pkgInfo = CTAN.get_package_info(dep.id)
        # Use pkg.name for normal pkgs, name of collection for packages that are in collection
        if 'topics' in pkgInfo and 'collections' in pkgInfo['topics']:
            ctan_path = pkgInfo['ctan']['path']
            # Problem: Last elem of ctan path is sometimes not pkg-name.
            # E.g. tikz, where ctan path is /graphics/pgf/base
            name = ctan_path.split('/')[-1]
        else:
            name = dep.name
    except KeyError:
        logger.debug(f"Using {dep.name} as fallback for folder name")
        name = dep.name

    download_folder = join(pkg_folder, name)
    zip_file_name = join(download_folder, basename(download_folder) + '.zip')

    # Download the ZIP file
    response = requests.get(url, allow_redirects=True)
    if not response.ok:
        raise DownloadError(response.text if hasattr(response, 'text') and response.text
                            else f'Cannot download {dep}: {response.reason}')

    os.makedirs(download_folder, exist_ok=True)
    logger.debug(f"Downloading files into {download_folder}")

    with open(zip_file_name, 'wb') as file:
        file.write(response.content)

    # Extract the ZIP file into a folder
    # This sometimes fails, but in those cases opening .zip with Windows doesn't work either.
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall(download_folder)

    # Organize and install the package's files
    os.remove(zip_file_name)
    organize_files(download_folder, tds=url.endswith('.tds.zip'))

    # Return the path to the folder
    return download_folder


def organize_files(folder_path: str, tds: bool):
    """Flatten folder, convert .ins/.dtx to .sty, unnecessary files/folders are deleted

    Args:
        folder_path (str): Path of folder to organize
        tds (bool): Is content of folder_path organized according to TeX Directory Structure Guidelines?

    Raises:
        OSError: folder_path is not a valid folder
    """

    if not exists(folder_path):
        raise OSError(f"Error while cleaning up download folder: {folder_path} is not a valid path")

    files_path = folder_path

    # If a package follows TDS, we only need the files in subfolder 'tex'
    # and don't need to try and build the source files
    if tds:
        # TDS-packaged packages (TEX Directory Standard) follow a certain folder structure:
        #   The subfolder 'tex' contains the built files that latex uses, other folders contain
        #   the source code and documentation
        #   For more information, see https://ctan.org/TDS-guidelines

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

    # Remove the subfolders
    folders = []
    for f in os.listdir(folder_path):
        path = join(folder_path, f)
        if isdir(path):
            folders.append(path)
    for folder in folders:
        shutil.rmtree(folder)

    # Only style-files left, nothing to install
    if tds:
        return

    # Convert .ins and .dtx to .sty and .cls
    old_cwd = os.getcwd()
    os.chdir(folder_path)
    ins_files = [abspath(file) for file in os.listdir() if isfile(abspath(file)) and file.endswith('.ins')]
    dtx_files = [abspath(file) for file in os.listdir() if isfile(abspath(file)) and file.endswith('.dtx')]

    # Install .ins files
    if len(ins_files) > 0:
        for ins_file in ins_files:
            name = (basename(ins_file)).split('.')[0]
            logger.debug(f"Creating sty-files from {basename(ins_file)}")

            try:
                # In case of sty-file already existing, enter 'n' instead of waiting for timeout.
                # Problem: There's also cases where prompt is for something else, where I do not want to say 'n'
                subprocess.run(['latex', basename(ins_file)], stdout=subprocess.DEVNULL, timeout=3, input=b'n\n')
            except Exception as e:
                # Possible reasons for timeout: File should not be executed, .sty file already exists etc.
                logger.warning(f"Problem while installing {name}.ins: {e}")
    # Install dtx files only if no ins-files found
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
