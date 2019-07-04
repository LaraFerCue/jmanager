from pathlib import PosixPath
from tarfile import TarFile

from models.distribution import Distribution
from models.jail import Jail
from src.utils.zfs import ZFS


class JailFactory:
    ZFS_FACTORY = ZFS()

    def __init__(self, jail_root_path: PosixPath, zfs_root_data_set: str):
        self._jail_root_path = jail_root_path
        self._zfs_root_data_set = zfs_root_data_set

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

    def jail_exists(self, distribution: Distribution):
        list_of_datasets = self.ZFS_FACTORY.zfs_list(
            f"{self._zfs_root_data_set}/{distribution.version}_{distribution.architecture.value}")
        return len(list_of_datasets) > 0

    def create_jail(self, jail_data: Jail, distribution: Distribution, path_to_tarballs: PosixPath):
        pass
