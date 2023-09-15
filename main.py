
from argparse import _SubParsersAction, ArgumentParser
import os
from typing import Type, get_type_hints

from src.core.lpm import lpm

def add_install_parser(subparsers):
    # Create sub-parser for the install command
    install_parser = subparsers.add_parser('install', help='Install package(s)')
    install_parser.add_argument('-v', '--version', type=str, help='Version to install: Either number (e.g. 1.2a) or date (YYYY/MM/DD)', metavar="")
    install_parser.add_argument('-y', '--yes_to_prompts', action='store_true', help='If provided, answer all prompts with yes')

    mutual_excl_args = install_parser.add_mutually_exclusive_group(required=True)
    mutual_excl_args.add_argument('package', default=None, nargs='?', help='Package id to install')
    mutual_excl_args.add_argument('--lockfile', action='store_true', help='Install packages from lockfile')
    add_debug_option(install_parser)

def add_upgrade_parser(subparsers):
    # Create sub-parser for the upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='upgrade package(s) to newest version')
    mutual_excl_args = upgrade_parser.add_mutually_exclusive_group(required=True)

    mutual_excl_args.add_argument('-p', '--package', type=str, help='upgrade specific package', metavar="")
    mutual_excl_args.add_argument('-a', '--all',action='store_true', help='upgrade all packages')
    add_debug_option(upgrade_parser)
    

def add_init_parser(subparsers):
    init_parser = subparsers.add_parser('init', help='Initialize a new project')
    init_parser.add_argument('-i', '--dockerimage', type=str, help='Name/ID of Docker Image to use. Will be used to compile your TeX files', metavar="")
    
def add_list_parser(subparsers):
    # Create sub-parser for the install command
    list_parser = subparsers.add_parser('list', help='List installed package(s)')
    list_parser.add_argument('-tree', '--tree', action='store_true', help='Show dependencies as tree')
    list_parser.add_argument('-top', '--toplevel', action='store_true', help='Only show packages directly installed by user')
    
def add_remove_parser(subparsers):
    remove_parser = subparsers.add_parser('remove', help='Uninstall a package from project')
    remove_parser.add_argument('package', type=str, help='Id of package to remove', metavar="")
    add_debug_option(remove_parser)

def add_build_parser(subparsers):
    build_parser = subparsers.add_parser('build', help='Build your project')
    build_parser.add_argument('build_args', help='Build command to execute', nargs="+")

def add_debug_option(parser):
    parser.add_argument('-debug', action='store_true', help='Set logging level to debug instead of info')

def handle_input(args):
    try:
        lpm_inst = lpm(args.debug)
    except AttributeError:
        lpm_inst = lpm()

    if args.command == 'install':
        if args.package:
            lpm_inst.install_pkg(args.package, args.version, args.yes_to_prompts)
        elif args.lockfile:
            if args.version:
                print("WARN: Version will be ignored since --lockfile was given")
            lpm_inst.install()
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
        if args.dockerimage:
            lpm_inst.init(args.dockerimage)
        else:
            lpm_inst.init()
    elif args.command == 'list':
        lpm_inst.list_packages(args.toplevel, args.tree)
    elif args.command == 'build':
        lpm_inst.build(args.build_args)
    else:
        print("Command not recognized. Please use -h for to see the available commands")

def main():
    print(f" -- lpm called from {os.getcwd()} -- \n")
    parser = ArgumentParser(prog='lpm')
    
    # Create all subparsers
    subparsers = parser.add_subparsers(dest='command')
    add_install_parser(subparsers)
    add_upgrade_parser(subparsers)
    add_remove_parser(subparsers)
    add_build_parser(subparsers)
    add_init_parser(subparsers)
    add_list_parser(subparsers)

    # Set the function to be called when the command is run
    parser.set_defaults(func=handle_input)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

