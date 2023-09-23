import os
import platform
system = platform.system().lower()

print("Setting up lpm installation")

if not os.path.exists('venv'):
    print("Please create a virtual environment using the name 'venv' and try again")
    exit
    
# Add folder to PATH
if system == 'windows':
    with open("lpm.bat", "w") as f:
        content = [
            ":: This file is used to execute lpm from anywhere. Please make sure that the parent folder of this file is in PATH", 
            "",
            "./venv/Scripts/activate",
            f"@python {os.path.join(os.getcwd(), 'main.py')} %*"
            ]
        f.write("\n".join(content))

    # TODO: Figure out how to append cwd to PATH here, or else ask user to do it manually. os.environ["PATH"] += doesn't persist changes
    
    print(f"Please add {os.getcwd()} to PATH so that you can use lpm from anywhere")

    # my_path = os.getcwd()
    # new_path = my_path  + os.pathsep + os.environ["PATH"]
    # print(f"Adding {my_path} to PATH...")
    # os.environ["PATH"] = new_path

if system == 'linux':
    print("... Creating executable shell script")

    # Create file that holds necessary commands to execute lpm
    with open("lpm", "w") as f:
        content = [
            '#!/bin/bash',
            '',
            "source venv/bin/activate",
            f'python {os.path.join(os.getcwd(), "main.py")} "$@"' # "$@" so that arguments are passed
            ]
        f.write("\n".join(content))

    if not os.path.exists('lpm'):
        print("Couldn't create lpm shell file.")
        exit
    
    # Make executable
    os.chmod('lpm', 0o755)  # Equivalent to 'chmod +x' in Linux

    # Move file to bin
    src, dest = os.path.abspath('lpm'), os.path.join('/usr', 'local', 'bin', 'lpm')
    print("... Moving executable to " + dest)
    os.rename(src, dest)

    print("Setup of lpm finished\nType 'lpm -h' anywhere to get started")

if system == 'darwin': # darwin = MacOS
    print("Your system is not yet supported\nFor manual use, execute 'python main.py'")
    pass

# TODO: Setup VPTAN here
