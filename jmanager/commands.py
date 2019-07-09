from argparse import Namespace
from pathlib import PosixPath
from typing import Dict

from jmanager.jail_manager import JailManager
from src.configuration import read_configuration_file, parse_jmanagerfile
from src.factories.base_jail_factory import BaseJailFactory
from src.factories.jail_factory import JailFactory
from src.utils.fetch import HTTPFetcher

LIST_HEADER = "JAIL\tBASE JAIL"


def create_command(jmanagerfile: str, jail_manager: JailManager):
    jmanagerfile_path = PosixPath(jmanagerfile)
    jmanagerfile_list = parse_jmanagerfile(read_configuration_file(jmanagerfile_path))

    for jmanagerfile in jmanagerfile_list:
        jail_manager.create_jail(jail_data=jmanagerfile.jail, distribution=jmanagerfile.distribution)


def execute_commands(args: Namespace):
    config_file_path = PosixPath(args.jmanager_config)
    configuration: Dict[str, str] = read_configuration_file(config_file_path)
    base_jail_factory = BaseJailFactory(jail_root_path=PosixPath(configuration['jail_base_path']),
                                        zfs_root_data_set=configuration['zfs_root_dataset'])
    jail_factory = JailFactory(
        base_jail_factory=base_jail_factory,
        jail_config_folder=PosixPath(configuration['jmanager_config_dir'])
    )

    jail_manager = JailManager(http_fetcher=HTTPFetcher(),
                               jail_factory=jail_factory)

    if args.command == 'create':
        create_command(jail_manager=jail_manager, jmanagerfile=args.jmanagerfile)
    elif args.command == 'destroy':
        jail_manager.destroy_jail(args.jail_name)
    elif args.command == 'list':
        print_list_of_jails(jail_manager=jail_manager)


def print_list_of_jails(jail_manager: JailManager):
    print(LIST_HEADER)
    for jail in jail_manager.list_jails():
        print(f"{jail.name}\t{jail.origin}")
