import os
import shutil
from argparse import Namespace
from pathlib import PosixPath
from typing import Dict

from jmanager.commands.create import create_command
from jmanager.commands.list import print_list_of_jails, list_command
from jmanager.factories.base_jail_factory import BaseJailFactory
from jmanager.factories.data_set_factory import DataSetFactory
from jmanager.factories.jail_factory import JailFactory
from jmanager.jail_manager import JailManager
from jmanager.utils.fetch import HTTPFetcher
from src.configuration import read_configuration_file


def execute_commands(args: Namespace):
    config_file_path = PosixPath(args.jmanager_config)
    configuration: Dict[str, str] = read_configuration_file(config_file_path)
    jail_root_path = PosixPath(configuration['jail_base_path'])
    jail_config_folder = PosixPath(configuration['jmanager_config_dir'])

    initialize_program(jail_config_folder, jail_root_path)

    data_set_factory = DataSetFactory(zfs_root_data_set=configuration['zfs_root_dataset'])
    base_jail_factory = BaseJailFactory(jail_root_path=jail_root_path,
                                        data_set_factory=data_set_factory)
    jail_factory = JailFactory(
        base_jail_factory=base_jail_factory,
        jail_config_folder=jail_config_folder
    )

    jail_manager = JailManager(http_fetcher=HTTPFetcher(),
                               jail_factory=jail_factory)

    if args.command == 'create':
        create_command(jail_manager=jail_manager, jmanagerfile=args.jmanagerfile)
    elif args.command == 'destroy':
        jail_manager.destroy_jail(args.jail_name)
    elif args.command == 'list':
        list_command(list_type=args.type, jail_manager=jail_manager)
    elif args.command == 'start':
        jail_manager.start(jail_name=args.jail_name)
    elif args.command == 'stop':
        jail_manager.stop(jail_name=args.jail_name)
    elif args.command == 'configure':
        jail_manager.configure_jail(jail_name=args.jail_name)


def initialize_program(jail_config_folder: PosixPath, jail_root_path: PosixPath):
    if not jail_root_path.is_dir():
        if jail_root_path.exists():
            shutil.rmtree(jail_root_path.as_posix(), ignore_errors=True)
        os.makedirs(jail_root_path.as_posix(), exist_ok=True)
    if not jail_config_folder.is_dir():
        if jail_config_folder.exists():
            shutil.rmtree(jail_config_folder.as_posix(), ignore_errors=True)
        os.makedirs(jail_config_folder.as_posix(), exist_ok=True)
