from src.core.lpm import lpm
import os
import shutil

# Clean previous run
packages_folder = r"C:\Users\Domin\Documents\UZH_Docs\BA\code\Prototype\packages"
if os.path.exists(packages_folder):
    shutil.rmtree(packages_folder)


# lpm.install(os.path.join(os.getcwd(), "requirements-lock.json"))

lpm.install_pkg("acro")