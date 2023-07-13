# Latex Package Manager
## Setup
### Windows
1. Clone this repository using git clone \<repo-url\>
2. Go into directory `/latexpm` where setup.py is
3. In command line, enter `python setup.py`. This will create a .bat file which enables you to use the package manager in any directory you want.

## Usage
### Create a new project
1. Head to directory where your `.tex` file lives
2. In command line, enter `lpm init`. This will create the necessary files for the package manager to work.

### Install a package
`lpm install \<package-id\>`

### Install all packages from Lockfile
`lpm install --lockfile`

