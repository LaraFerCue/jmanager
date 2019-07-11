import os
import shutil
import subprocess
from distutils.file_util import copy_file
from pathlib import PosixPath
from typing import Dict, List

from models.distribution import Distribution, Version
from models.jail import Jail, JailOption, JailError
from src.factories.base_jail_factory import BaseJailFactory


class JailFactory:
    JAIL_CMD = "jail"

    DEFAULT_JAIL_OPTIONS: Dict[JailOption, str] = {
        JailOption.PATH: '',
        JailOption.HOSTNAME: '',
        JailOption.OS_RELEASE: '',
        JailOption.EXEC_START: 'sh /etc/rc',
        JailOption.EXEC_STOP: 'sh /etc/rc.shutdown',
        JailOption.IP4: 'inherit'
    }

    def __init__(self, base_jail_factory: BaseJailFactory, jail_config_folder: PosixPath):
        self._jail_config_folder = jail_config_folder
        self._base_jail_factory = base_jail_factory

    @property
    def base_jail_factory(self) -> BaseJailFactory:
        return self._base_jail_factory

    def get_jail_default_options(self, jail_data: Jail, os_version: Version) -> Dict[JailOption, str]:
        jail_options = self.DEFAULT_JAIL_OPTIONS.copy()
        jail_options[JailOption.PATH] = self._base_jail_factory.get_jail_mountpoint(jail_data.name).as_posix()
        jail_options[JailOption.HOSTNAME] = jail_data.name
        jail_options[JailOption.OS_RELEASE] = str(os_version)
        jail_options.update(jail_data.options)
        return jail_options

    def create_jail(self, jail_data: Jail, distribution: Distribution):
        if not self._base_jail_factory.base_jail_exists(distribution=distribution):
            raise JailError(f"The base jail for version {distribution} does not exist.")

        if self._jail_config_folder.joinpath(jail_data.name).is_dir():
            raise JailError(f"The jail '{jail_data.name}' already exists.")

        if self._base_jail_factory.data_set_factory.base_data_set_exists(data_set_name=jail_data.name):
            raise JailError(f"The jail '{jail_data.name}' has some left overs, please remove them and try again.")

        self.clone_base_jail(distribution, jail_data.name)
        self.write_configuration_files(distribution, jail_data)

    def get_config_file_path(self, jail_name: str):
        jail_config_folder = self._jail_config_folder.joinpath(jail_name)
        config_file = jail_config_folder.joinpath('jail.conf')
        return config_file

    def write_configuration_files(self, distribution, jail_data):
        jail_config_folder = self._jail_config_folder.joinpath(jail_data.name)
        if not jail_config_folder.is_dir():
            os.makedirs(jail_config_folder.as_posix())

        jail_options = self.get_jail_default_options(jail_data, distribution.version)
        final_jail = Jail(name=jail_data.name, options=jail_options)
        final_jail.write_config_file(self.get_config_file_path(jail_data.name))
        distribution.write_config_file(jail_config_folder.joinpath('distribution.conf'))

    def clone_base_jail(self, distribution, jail_data_set):
        jail_mountpoint = self._base_jail_factory.get_jail_mountpoint(jail_data_set)

        clone_properties: Dict[str, str] = {"mountpoint": jail_mountpoint.as_posix()}
        snapshot_name = self._base_jail_factory.get_snapshot_name(component_list=distribution.components)
        self._base_jail_factory.data_set_factory.clone(
            data_set_name=self._base_jail_factory.get_data_set_name(distribution),
            snapshot_name=snapshot_name,
            clone_data_set_name=jail_data_set,
            options=clone_properties)

    def jail_exists(self, jail_name: str) -> bool:
        configuration_file = self.get_config_file_path(jail_name)
        distribution = self._jail_config_folder.joinpath(jail_name, 'distribution.conf')
        return configuration_file.is_file() and distribution.is_file()

    def destroy_jail(self, jail_name: str):
        jail_config_dir = self._jail_config_folder.joinpath(jail_name)
        shutil.rmtree(jail_config_dir.as_posix())

        self._base_jail_factory.data_set_factory.delete_data_set(jail_name)

    def start_jail(self, jail_name: str) -> str:
        jail_config_file = self._jail_config_folder.joinpath(f"{jail_name}.conf")
        cmd = f"{self.JAIL_CMD} -f {jail_config_file} -c {jail_name}"
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, check=True,
                              universal_newlines=True).stdout

    def stop_jail(self, jail_name: str):
        jail_config_file = self._jail_config_folder.joinpath(f"{jail_name}.conf")
        cmd = f"{self.JAIL_CMD} -f {jail_config_file} -r {jail_name}"
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, check=True,
                              universal_newlines=True).stdout

    def list_jails(self) -> List[Jail]:
        jail_list = []
        for config_folder in self._jail_config_folder.iterdir():
            if config_folder.joinpath('jail.conf').is_file():
                jail = Jail.read_jail_config_file(config_folder.joinpath('jail.conf'))
                jail.origin = Distribution.read_config_file(config_folder.joinpath('distribution.conf'))
                jail_list.append(jail)
        return jail_list
