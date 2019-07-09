import subprocess
from pathlib import PosixPath
from typing import Dict, List

from models.distribution import Distribution, Version, Architecture
from models.jail import Jail, JailOption, JailError
from src.factories.base_jail_factory import BaseJailFactory
from src.utils.zfs import ZFS


class JailFactory:
    ZFS_FACTORY = ZFS()
    SNAPSHOT_NAME = "jmanager_base_jail"
    JAIL_CMD = "jail"

    DEFAULT_JAIL_OPTIONS: Dict[JailOption, str] = {
        JailOption.PATH: '',
        JailOption.HOSTNAME: '',
        JailOption.OS_RELEASE: '',
        JailOption.EXEC_START: 'sh /etc/rc',
        JailOption.EXEC_STOP: 'sh /etc/rc.shutdown',
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

    def create_jail(self, jail_data: Jail, os_version: Version, architecture: Architecture):
        distribution = Distribution(version=os_version, architecture=architecture, components=[])
        if not self._base_jail_factory.base_jail_exists(distribution=distribution):
            raise JailError(f"The base jail for version {os_version}/{architecture.value} does not exist.")

        if self._jail_config_folder.joinpath(f"{jail_data.name}.conf").is_file():
            raise JailError(f"The jail '{jail_data.name}' already exists.")

        jail_data_set = self._base_jail_factory.get_jail_data_set(jail_data.name)
        if len(self.ZFS_FACTORY.zfs_list(data_set=jail_data_set)) > 0:
            raise JailError(f"The jail '{jail_data.name}' has some left overs, please remove them and try again.")

        base_jail_dataset = self._base_jail_factory.get_base_jail_data_set(distribution=distribution)
        jail_mountpoint = self._base_jail_factory.get_jail_mountpoint(jail_data_set)
        clone_properties: Dict[str, str] = {"mountpoint": jail_mountpoint.as_posix()}
        self.ZFS_FACTORY.zfs_clone(snapshot=f"{base_jail_dataset}@{self.SNAPSHOT_NAME}",
                                   data_set=jail_data_set,
                                   options=clone_properties)

        jail_options = self.get_jail_default_options(jail_data, os_version)
        final_jail = Jail(name=jail_data.name, options=jail_options)
        final_jail.write_config_file(self._jail_config_folder.joinpath(f"{jail_data.name}.conf"))

    def jail_exists(self, jail_name: str) -> bool:
        return self._jail_config_folder.joinpath(f"{jail_name}.conf").is_file()

    def destroy_jail(self, jail_name: str):
        self._jail_config_folder.joinpath(f"{jail_name}.conf").unlink()
        self.ZFS_FACTORY.zfs_destroy(self._base_jail_factory.get_jail_data_set(jail_name))

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
        for config_file in self._jail_config_folder.iterdir():
            if config_file.suffix == '.conf':
                jail = Jail.read_jail_config_file(config_file)

                jail.origin = self._base_jail_factory.get_origin_from_jail(jail.name)
                jail_list.append(jail)
        return jail_list
