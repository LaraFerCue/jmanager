from pathlib import PosixPath
from tarfile import TarFile
from typing import Dict

from models.distribution import Distribution, Version, Architecture
from models.jail import Jail, JailOption
from src.utils.zfs import ZFS


class JailFactory:
    ZFS_FACTORY = ZFS()
    SNAPSHOT_NAME = "jmanager_base_jail"
    DEFAULT_JAIL_OPTIONS: Dict[JailOption, str] = {
        JailOption.PATH: '',
        JailOption.HOSTNAME: '',
        JailOption.OS_RELEASE: '',
        JailOption.OS_REL_DATE: '',
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
        for component in distribution.components:
            if not path_to_tarballs.joinpath(f"{component.value}.txz").is_file():
                raise FileNotFoundError(f"Component '{component.value}' not found in {path_to_tarballs}")

        jail_path = f"{distribution.version}_{distribution.architecture.value}"
        self.ZFS_FACTORY.zfs_create(
            data_set=f"{self._zfs_root_data_set}/{jail_path}",
            options={"mountpoint": f"{self._jail_root_path}/{jail_path}"}
        )

        for component in distribution.components:
            with TarFile(path_to_tarballs.joinpath(f"{component.value}.txz").as_posix()) as tarfile:
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

    def create_jail(self, jail_data: Jail, os_version: Version, architecture: Architecture):
        base_jail_dataset = f"{self._zfs_root_data_set}/{os_version}_{architecture.value}"
        self.ZFS_FACTORY.zfs_clone(snapshot=f"{base_jail_dataset}@{self.SNAPSHOT_NAME}",
                                   data_set=f"{self._zfs_root_data_set}/{jail_data.name}",
                                   options={})
        jail_options = self.DEFAULT_JAIL_OPTIONS.copy()
        jail_options.update(jail_data.options)

        final_jail = Jail(name=jail_data.name, options=jail_options)
        final_jail.write_config_file(self._jail_config_folder.joinpath(f"{jail_data.name}.conf"))
