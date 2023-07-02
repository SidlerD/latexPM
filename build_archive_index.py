import os
import re
import subprocess
import requests
import json

repo_path = r"C:\Users\Domin\Documents\UZH_Docs\BA\code\test_git_archive\CTAN"
pkgs_path = r"C:\Users\Domin\Documents\UZH_Docs\BA\code\test_git_archive\CTAN\macros\latex"
packages_file = "TL_packages.json"


def get_packages_list():
    res = requests.get("http://www.ctan.org/json/2.0/packages").json()

    index = {}
    for pkg in res:
        # if pkg['name'] != pkg['key']:
        index[pkg['name']] = pkg['key']


    with open(packages_file, "w", encoding='utf-8') as f:
        f.write(json.dumps(index))


def extract_versions(index, commit_hash):
    """Assumes that all packages are in subfolder /macros/latex/"""
    # Get paths for all dtx and sty files
    paths = []
    for dir in os.listdir(os.path.join(pkgs_path, "contrib")) + os.listdir(os.path.join(pkgs_path, "exptl")) + os.listdir(os.path.join(pkgs_path, "required")):
        relevant_files = [os.path.join(dir, file) for file in os.listdir(dir) if (file.endswith('.sty') or file.endswith('.dtx'))]
        paths.extend(relevant_files)
    for file in os.listdir(os.path.join(pkgs_path, "base")):
        if file.endswith('.sty') or file.endswith('.dtx'):
            paths.append(os.path.abspath(file))
        
    # For each package_id in TL_packages.json: Find sty/dtx file path, read it/them, extract version
    with open(packages_file, "r") as f:
        cont = f.read()
        name_to_id = json.loads(cont) # List of all packages on CTAN
    
    # TODO: Some also use ProvideExplPackage, e.g.l3keys2e or acro
    pattern = r'\\ProvidesPackage\{(.*?)\}\[(.*?)\]'
    for pkg_name in name_to_id: # For each package:
        pkg_id = name_to_id[pkg_name]
        files = [path for path in paths if os.path.basename(path).startswith(pkg_name)] # Get all filepaths that end in packagename ...
        for file in files:
            with open(file, "r") as f:
                match = re.search(pattern, f.read())
                if match:
                    pkg_version = match.group(2) # ... and extract their version
                    index[commit_hash][pkg_id][os.path.basename(file)] = pkg_version





# Change directory to the repository path
os.chdir(repo_path)

# Get a list of all commit hashes
commit_hashes = subprocess.check_output(['git', 'rev-list', 'HEAD']).decode().splitlines()
print(commit_hashes)

index = {}

# Iterate over each commit hash
for commit_hash in commit_hashes:
    subprocess.call(['git', 'checkout', commit_hash])  # Checkout the commit
    extract_versions(index, commit_hash)


# Return to the latest commit
subprocess.call(['git', 'checkout', 'master'])
