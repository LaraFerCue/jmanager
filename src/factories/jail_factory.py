import subprocess
from pathlib import PosixPath
from tarfile import TarFile
from typing import Dict

from models.distribution import Distribution, Version, Architecture
from models.jail import Jail, JailOption
from src.utils.zfs import ZFS


class JailError(BaseException):
    pass


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

    def __init__(self, jail_root_path: PosixPath, zfs_root_data_set: str, jail_config_folder: PosixPath):
        self._jail_root_path = jail_root_path
        self._zfs_root_data_set = zfs_root_data_set
        self._jail_config_folder = jail_config_folder

        if jail_root_path.exists() and not jail_root_path.is_dir():
            raise PermissionError("The jail root path exists and it is not a directory")
        elif not jail_root_path.exists():
            jail_root_path.mkdir(parents=True)

    def create_base_jail(self, distribution: Distribution, path_to_tarballs: PosixPath):
        if self.base_jail_exists(distribution=distribution):
            raise JailError(f"The base jail for '{distribution.version}/{distribution.architecture.value}' exists")

        if self.base_jail_incomplete(distribution=distribution):
            raise JailError(f"The base jail '{distribution.version}/{distribution.architecture.value}' has left " + \
                            "overs, delete them and try again.")

        for component in distribution.components:
            if not path_to_tarballs.joinpath(f"{component.value}.txz").is_file():
                raise FileNotFoundError(f"Component '{component.value}' not found in {path_to_tarballs}")

        jail_path = f"{distribution.version}_{distribution.architecture.value}"
        self.ZFS_FACTORY.zfs_create(
            data_set=f"{self._zfs_root_data_set}/{jail_path}",
            options={"mountpoint": f"{self._jail_root_path}/{jail_path}"}
        )

        for component in distribution.components:
            with TarFile(path_to_tarballs.joinpath(f"{component.value}.txz").as_posix(), mode='r') as tarfile:
                tarfile.extractall(path=f"{self._jail_root_path}/{jail_path}")
        self.ZFS_FACTORY.zfs_snapshot(f"{self._zfs_root_data_set}/{jail_path}", snapshot_name=self.SNAPSHOT_NAME)

    def destroy_base_jail(self, distribution: Distribution):
        base_jail_dataset = f"{self._zfs_root_data_set}/{distribution.version}_{distribution.architecture.value}"
        if self.base_jail_exists(distribution=distribution):
            self.ZFS_FACTORY.zfs_destroy(data_set=f"{base_jail_dataset}@{self.SNAPSHOT_NAME}")
        if self.base_jail_incomplete(distribution=distribution):
            self.ZFS_FACTORY.zfs_destroy(data_set=f"{base_jail_dataset}")

    def base_jail_incomplete(self, distribution: Distribution):
        base_jail_dataset = f"{self._zfs_root_data_set}/{distribution.version}_{distribution.architecture.value}"
        return not self.base_jail_exists(distribution) and len(self.ZFS_FACTORY.zfs_list(base_jail_dataset))

    def base_jail_exists(self, distribution: Distribution):
        base_jail_dataset = f"{self._zfs_root_data_set}/{distribution.version}_{distribution.architecture.value}"
        list_of_datasets = self.ZFS_FACTORY.zfs_list(f"{base_jail_dataset}@{self.SNAPSHOT_NAME}")
        return len(list_of_datasets) > 0

    def get_jail_default_options(self, jail_data: Jail, os_version: Version) -> Dict[JailOption, str]:
        jail_options = self.DEFAULT_JAIL_OPTIONS.copy()
        jail_options[JailOption.PATH] = self._jail_root_path.joinpath(jail_data.name).as_posix()
        jail_options[JailOption.HOSTNAME] = jail_data.name
        jail_options[JailOption.OS_RELEASE] = str(os_version)
        jail_options.update(jail_data.options)
        return jail_options

    def create_jail(self, jail_data: Jail, os_version: Version, architecture: Architecture):
        base_jail_dataset = f"{self._zfs_root_data_set}/{os_version}_{architecture.value}"
        distribution = Distribution(version=os_version, architecture=architecture, components=[])
        if not self.base_jail_exists(distribution=distribution):
            raise JailError(f"The base jail for version {os_version}/{architecture.value} does not exist.")

        if self._jail_config_folder.joinpath(f"{jail_data.name}.conf").is_file():
            raise JailError(f"The jail '{jail_data.name}' already exists.")

        if len(self.ZFS_FACTORY.zfs_list(data_set=f"{self._zfs_root_data_set}/{jail_data.name}")) > 0:
            raise JailError(f"The jail '{jail_data.name}' has some left overs, please remove them and try again.")

        jail_mountpoint = self._jail_root_path.joinpath(jail_data.name)
        clone_properties: Dict[str, str] = {"mountpoint": jail_mountpoint.as_posix()}
        self.ZFS_FACTORY.zfs_clone(snapshot=f"{base_jail_dataset}@{self.SNAPSHOT_NAME}",
                                   data_set=f"{self._zfs_root_data_set}/{jail_data.name}",
                                   options=clone_properties)

        jail_options = self.get_jail_default_options(jail_data, os_version)
        final_jail = Jail(name=jail_data.name, options=jail_options)
        final_jail.write_config_file(self._jail_config_folder.joinpath(f"{jail_data.name}.conf"))

    def destroy_jail(self, jail_name: str):
        self._jail_config_folder.joinpath(f"{jail_name}.conf").unlink()
        self.ZFS_FACTORY.zfs_destroy(f"{self._zfs_root_data_set}/{jail_name}")

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
