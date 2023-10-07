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
            r'@echo off',
            r':: "%~dp0" expands to full path to folder containing this .bat-file'
            r':: Activate the virtual environment',
            r':: "2>nul" hides output from user when /venv is not found: Makes it possible to install requirements.txt globally, although discouraged',
            r':: powershell.exe: Which file to execute to run venv depends on whether cmd or powershell is used. Instead of checking manually, we just call powershell',
            r'powershell.exe ". %~dp0\venv\Scripts\Activate.ps1" 2>nul',
            r":: Run the Python script from lpm's directory",
            r'python "%~dp0\main.py" %*',
            r':: Do I need to Deactivate the virtual environment?? ',
            ]
        f.write("\n".join(content))

    print(f"Please add {os.getcwd()} to PATH so that you can use lpm from anywhere")


if system == 'linux':
    print("... Creating executable shell script")

    # Create file that holds necessary commands to execute lpm
    with open("lpm", "w") as f:
        content = [
            '#!/bin/bash',
            '',
            f"source {os.getcwd()}/venv/bin/activate",
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
