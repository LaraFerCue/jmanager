#!/usr/bin/env python3

import argparse
from pathlib import PosixPath
from typing import Dict

from jmanager.jail_manager import JailManager
from src.configuration import read_configuration_file, parse_jmanagerfile
from src.factories.jail_factory import JailFactory
from src.utils.fetch import HTTPFetcher

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

args = parser.parse_args()

config_file_path = PosixPath(args.jmanager_config)
configuration: Dict[str, str] = read_configuration_file(config_file_path)
jail_factory = JailFactory(
    jail_root_path=PosixPath(configuration['jail_base_path']),
    zfs_root_data_set=configuration['zfs_root_dataset'],
    jail_config_folder=PosixPath(configuration['jmanager_config_dir'])
)

jail_manager = JailManager(http_fetcher=HTTPFetcher(),
                           jail_factory=jail_factory)

if args.command == 'create':
    jmanagerfile_path = PosixPath(args.jmanagerfile)
    jmanagerfile_list = parse_jmanagerfile(read_configuration_file(jmanagerfile_path))

    for jmanagerfile in jmanagerfile_list:
        jail_manager.create_jail(jail_data=jmanagerfile.jail, distribution=jmanagerfile.distribution)
elif args.command == 'destroy':
    jail_manager.destroy_jail(args.jail_name)
