#!/usr/bin/env python3

import argparse

from jmanager.commands import execute_commands

parser = argparse.ArgumentParser(description="FreeBSD Jail Manager")
parser.add_argument("--jmanager-config", type=str,
                    help="path to the configuration file for the program",
                    default='/usr/local/etc/jmanager.conf')

subparsers = parser.add_subparsers(help="sub-command help")
create_parser = subparsers.add_parser('create')
create_parser.set_defaults(command='create')
create_parser.add_argument("--jmanagerfile",
                           type=str,
                           help="path to the configuration file for the jail to create",
                           default="./Jmanagerfile")

destroy_parser = subparsers.add_parser('destroy')
destroy_parser.set_defaults(command='destroy')
destroy_parser.add_argument("jail_name", type=str, help="name of the jail to destroy")

list_parser = subparsers.add_parser('list')
list_parser.set_defaults(command="list")
list_parser.add_argument('-t', '--type', type=str, default='jail', required=False,
                         choices=['jail', 'base'],
                         help="type of options to show")

args = parser.parse_args()
execute_commands(args)
