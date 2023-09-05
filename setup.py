import os
import platform
system = platform.system().lower()

print("Setting up lpm installation")
# Add folder to PATH
if system == 'windows':
    with open("lpm.bat", "w") as f:
        content = [
            ":: This file is used to execute lpm from anywhere. Please make sure that the parent folder of this file is in PATH", 
            "",
            f"@python {os.path.join(os.getcwd(), 'main.py')} %*"
            ]
        f.write("\n".join(content))

    # TODO: Figure out how to append cwd to PATH here, or else ask user to do it manually. os.environ["PATH"] += doesn't persist changes
    
    # my_path = os.getcwd()
    # new_path = my_path  + os.pathsep + os.environ["PATH"]
    # print(f"Adding {my_path} to PATH...")
    # os.environ["PATH"] = new_path

if system == 'linux':
    pass
if system == 'darwin': # darwin = MacOS
    pass

# URGENT: Setup VPTAN here
# Could host image with VPTAN on Docker hub, that would make it easy to install on all systems. No overhead since Docker is needed for build anyway