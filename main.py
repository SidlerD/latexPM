
from argparse import _SubParsersAction, ArgumentParser
import os
from typing import Type, get_type_hints

from src.core.lpm import lpm

def add_install_parser(subparsers):
    # Create sub-parser for the install command
    install_parser = subparsers.add_parser('install', help='Install package(s)')
    install_parser.add_argument('-v', '--version', type=str, help='Version to install: Either number (e.g. 1.2a) or date (YYYY/MM/DD)', metavar="")
    
    mutual_excl_args = install_parser.add_mutually_exclusive_group(required=True)
    mutual_excl_args.add_argument('package', default=None, nargs='?', help='Package id to install')
    mutual_excl_args.add_argument('--lockfile', action='store_true', help='Install packages from lockfile')
    mutual_excl_args.add_argument('--list', action='store_true', help='List all installed packages')
    add_debug_option(install_parser)

def add_upgrade_parser(subparsers):
    # Create sub-parser for the upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='upgrade package(s) to newest version')
    mutual_excl_args = upgrade_parser.add_mutually_exclusive_group(required=True)

    mutual_excl_args.add_argument('-p', '--package', type=str, help='upgrade specific package', metavar="")
    mutual_excl_args.add_argument('-a', '--all',action='store_true', help='upgrade all packages')
    add_debug_option(upgrade_parser)
    

def add_init_parser(subparsers):
    subparsers.add_parser('init', help='Initialize a new project')
    
def add_remove_parser(subparsers):
    remove_parser = subparsers.add_parser('remove', help='Uninstall a package from project')
    remove_parser.add_argument('package', type=str, help='Id of package to remove', metavar="")
    add_debug_option(remove_parser)

def add_debug_option(parser):
    parser.add_argument('-debug', action='store_true', help='Set logging level to debug instead of info')

def handle_input(args):
    lpm_inst = lpm(args.debug)

    if args.command == 'install':
        if args.package:
            lpm_inst.install_pkg(args.package, args.version)
        elif args.lockfile:
            if args.version:
                print(f"WARN: Version will be ignored since --lockfile was given")
            lpm_inst.install()
        elif args.list:
            if args.version:
                print(f"WARN: Version will be ignored since --list was given")
            lpm_inst.list_packages()
    elif args.command == 'upgrade':
        if args.package:
            lpm_inst.upgrade_pkg(args.package)
        elif args.all:
            lpm_inst.upgrade()
    elif args.command == 'remove':
        if args.package:
            lpm_inst.remove(args.package)
        else:
            print("Package-id needed to remove")
    elif args.command == 'init':
        lpm_inst.init()
    else:
        print("Command not recognized. Please use -h for to see the available commands")

def main():
    print(f" -- lpm called from {os.getcwd()} -- \n")
    parser = ArgumentParser(prog='lpm')
    
    # Create all subparsers
    subparsers = parser.add_subparsers(dest='command')
    add_install_parser(subparsers)
    add_upgrade_parser(subparsers)
    add_init_parser(subparsers)
    add_remove_parser(subparsers)

    # Set the function to be called when the command is run
    parser.set_defaults(func=handle_input)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

