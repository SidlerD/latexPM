# Latex Package Manager
## Setup
1. Clone this repository: `git clone <repo-url>`
2. Go into the cloned directory: `cd latexPM` 
3. [Create and start a virtual environment](https://python.land/virtual-environments/virtualenv) with the name `venv` (Note: Use python 3.10 when creating venv)
4. Install lpm's dependencies: `pip install -r requirements.txt`
5. Run lpm's setup script: `python setup.py`

6. (Windows only): Add the absolute path to the `latexPM` folder [to PATH](https://linuxhint.com/add-directory-to-path-environment-variables-windows/)

6. [Setup VPTAN](https://github.com/SidlerD/VPTAN#setup)

- Additional: [Docker](https://docs.docker.com/get-docker/) and [latex](https://www.latex-project.org/get/) need to be installed on your system in order for lpm to complete it's tasks successfully. If you don't already have them installed, please do so before using lpm.

## Usage
### Get help / list all commands
- Use `lpm -h` to get a list of all commands that `lpm` provides
- Use `lpm <command> -h` to get the parameters and flags which that command takes
### Create a new project
1. Head to directory where your `.tex` file lives
2. In command line, enter `lpm init`. This will create the necessary files for the package manager to work.

### Install a package
`lpm install <package-id>`

### Install all packages from Lockfile
`lpm install --lockfile`

### Build your project
`lpm build pdflatex file.tex`: Use the command `pdflatex file.tex` to compile file.tex and get the resulting pdf in the same directory


### Other commands
For a full list of all available commands, please use `lpm -h`