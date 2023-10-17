# Latex Package Manager
## Setup
1. Clone this repository: `git clone <repo-url>`

2. Go into the cloned directory: `cd latexPM` 

3. [Create and start a virtual environment](https://python.land/virtual-environments/virtualenv) with the name `venv` (Note: Use python 3.10.2 when creating venv)

4. Install lpm's dependencies: `pip install -r requirements.txt`

5. Run lpm's setup script: `python setup.py` (You may need to use `sudo` and `python3` on Linux)

6. (Windows only): Add the absolute path to the `latexPM` folder [to PATH](https://linuxhint.com/add-directory-to-path-environment-variables-windows/)

7. [Setup VPTAN](https://github.com/SidlerD/VPTAN#setup)

- Additional: [Docker](https://docs.docker.com/get-docker/) and [latex](https://www.latex-project.org/get/) need to be installed on your system in order for lpm to complete it's tasks successfully. If you don't already have them installed, please do so before using lpm.


## First steps
1. Initialize a new project: `lpm init`
2. Install a package: `lpm install <pkg-id>`. Repeat until needed packages installed
3. Build your project: `lpm build <args>`, where `<args>` is the command used for building your project, e.g. `pdflatex file.tex`


## Sharing your project
One of lpm's core functionalities is the ability to reproduce your project and its environment on other machines and/or at different times. All the information lpm needs to do that is contained in your `requirements-lock.json` file.

1. Follow the steps in [First Steps](#first-steps). This will automatically create `requirements-lock.json` and keep it updated.
2. Copy `requirements-lock.json` and all your project-files (e.g. `.tex`, `.png` and similar) to a separate folder.
3. That folder now contains all that is needed to recreate your project using lpm. Share it with people or archive it for later use.

## Recreating a project
When given a folder that contains at least a `requirements-lock.json` (+ some project files usually), lpm can recreate the project described by `requirements-lock.json` with just one command:

1. Go into your project folder: `cd project_folder`
2. Recreate project: `lpm init`

    This automatically recognizes the presence of `requirements-lock.json` and does the following things:
    - Pull Docker Image specified in Lockfile
    - Create folder for installing packages into
    - Install all packages specified in Lockfile in exact same version

3. To build the project, you can now use `lpm build <args>` and provide the exact command you want to use to compile your project as `<args>`


## General Usage
### Get help / list all commands
- Use `lpm -h` to get a list of all commands that `lpm` provides
- Use `lpm <command> -h` to get the parameters and flags which that command takes


### Create a new project
1. Head to directory where your `.tex` file lives
2. In command line, enter `lpm init`. This will create the necessary files for the package manager to work and must always be the __first command__ of lpm __called in a new project__.

### Create a new project based on a lock file
1. Head to directory where your `requirements-lock.json` file is
2. Enter `lpm init`. This will detect the lockfile and recreate the environment described in it.

### Install a package
`lpm install <package-id>`

### Install all packages from Lockfile
`lpm install --lockfile`

### Build your project
`lpm build pdflatex file.tex`: Use the command `pdflatex file.tex` to compile file.tex and get the resulting pdf in the same directory. 

### List installed packages
`lpm list`: Use flag `--tree` to see the packages in the format of a dependency tree

### Other commands
For a full list of all available commands, please use `lpm -h`
