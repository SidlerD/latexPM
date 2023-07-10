
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

def add_upgrade_parser(subparsers):
    # Create sub-parser for the upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='upgrade package(s) to newest version')
    mutual_excl_args = upgrade_parser.add_mutually_exclusive_group(required=True)

    mutual_excl_args.add_argument('-p', '--package', type=str, help='upgrade specific package', metavar="")
    mutual_excl_args.add_argument('-a', '--all',action='store_true', help='upgrade all packages')
    

def handle_input(args):
    lpm_inst = lpm()

    print(os.getcwd())
    # TODO: This could be used to get path to pass to lpm, which needs it to read lockfile and install packages

    if args.command == 'install':
        if args.package:
            lpm_inst.install_pkg(args.package, args.version)
        elif args.lockfile:
            if args.version:
                print(f"WARN: Version will be ignored since --lockfile was given")
            lpm_inst.install()
    elif args.command == 'upgrade':
        if args.package:
            lpm_inst.upgrade_pkg(args.package)
        else:
            lpm_inst.upgrade()

def main():
    parser = ArgumentParser(prog='lpm')
    
    # Create all subparsers
    subparsers = parser.add_subparsers(dest='command')
    add_install_parser(subparsers)
    add_upgrade_parser(subparsers)
    

    # Set the function to be called when the command is run
    parser.set_defaults(func=handle_input)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

