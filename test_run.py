from src.core.lpm import lpm
import os
import shutil

# Clean previous run
packages_folder = os.path.join(os.getcwd(), "/packages")

if os.path.exists(packages_folder):
    shutil.rmtree(packages_folder)


# lpm.install(os.path.join(os.getcwd(), "requirements-lock.json"))

lpm.install_pkg("amsmath")