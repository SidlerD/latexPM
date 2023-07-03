from src.core.lpm import lpm
import os
import shutil

# Clean previous run
packages_folder = os.path.join(os.getcwd(), "/packages")

if os.path.exists(packages_folder):
    shutil.rmtree(packages_folder)



lpm_inst = lpm()

lpm_inst.install(os.path.join(os.getcwd(), "requirements-lock.json"))
lpm_inst.install_pkg("amsmath")