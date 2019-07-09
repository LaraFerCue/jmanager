import lzma
import tarfile
from pathlib import PosixPath
from tempfile import TemporaryDirectory

from models.distribution import Distribution, Component
from models.jail import JailError
from src.utils.zfs import ZFS


def extract_tarball_into(jail_path: PosixPath, path_to_tarball: PosixPath):
    with TemporaryDirectory(prefix="jail_factory_") as temp_dir:
        temp_file_path = f"{temp_dir}/{path_to_tarball.name}"
        with lzma.open(path_to_tarball.as_posix(), 'r') as lz_file:
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(lz_file.read())
        with tarfile.open(temp_file_path, mode='r') as tar_file:
            tar_file.extractall(path=jail_path.as_posix())


class BaseJailFactory:
    ZFS_FACTORY = ZFS()
    SNAPSHOT_NAME = "jmanager_base_jail"

    def __init__(self, jail_root_path: PosixPath, zfs_root_data_set: str):
        self._jail_root_path = jail_root_path
        self._zfs_root_data_set = zfs_root_data_set

        if jail_root_path.exists() and not jail_root_path.is_dir():
            raise PermissionError("The jail root path exists and it is not a directory")
        elif not jail_root_path.exists():
            jail_root_path.mkdir(parents=True)

    def base_jail_exists(self, distribution: Distribution):
        base_jail_dataset = self.get_base_jail_data_set(distribution)
        snapshot_data_set = f"{base_jail_dataset}@{self.get_snapshot_name(distribution=distribution)}"
        list_of_datasets = self.ZFS_FACTORY.zfs_list(data_set=snapshot_data_set)
        return len(list_of_datasets) > 0

    def get_snapshot_name(self, distribution: Distribution):
        components = distribution.components.copy()
        components.remove(Component.BASE)

        if not components:
            return self.SNAPSHOT_NAME
        component_extension = '_'.join([dist.value for dist in components])
        return f"{self.SNAPSHOT_NAME}_{component_extension}"

    def create_base_jail(self, distribution: Distribution, path_to_tarballs: PosixPath):
        if self.base_jail_exists(distribution=distribution):
            raise JailError(f"The base jail for '{distribution.version}/{distribution.architecture.value}' exists")

        if self.base_jail_incomplete(distribution=distribution):
            raise JailError(f"The base jail '{distribution.version}/{distribution.architecture.value}' has left " + \
                            "overs, delete them and try again.")

        for component in distribution.components:
            if not path_to_tarballs.joinpath(f"{component.value}.txz").is_file():
                raise FileNotFoundError(f"Component '{component.value}' not found in {path_to_tarballs}")

        jail_data_set_path = f"{distribution.version}_{distribution.architecture.value}"
        jail_path = self.get_jail_mountpoint(jail_data_set_path)
        self.ZFS_FACTORY.zfs_create(
            data_set=f"{self._zfs_root_data_set}/{jail_data_set_path}",
            options={"mountpoint": jail_path.as_posix()}
        )

        for component in set(distribution.components):
            extract_tarball_into(jail_path, path_to_tarballs.joinpath(f"{component.value}.txz"))
        self.ZFS_FACTORY.zfs_snapshot(f"{self._zfs_root_data_set}/{jail_data_set_path}",
                                      snapshot_name=self.get_snapshot_name(distribution=distribution))

    def get_jail_mountpoint(self, jail_data_set_path: str) -> PosixPath:
        jail_path = self._jail_root_path.joinpath(jail_data_set_path)
        return jail_path

    def destroy_base_jail(self, distribution: Distribution):
        base_jail_dataset = self.get_base_jail_data_set(distribution)
        if self.base_jail_exists(distribution=distribution):
            snapshot_name = self.get_snapshot_name(distribution=distribution)
            self.ZFS_FACTORY.zfs_destroy(data_set=f"{base_jail_dataset}@{snapshot_name}")
        if self.base_jail_incomplete(distribution=distribution):
            self.ZFS_FACTORY.zfs_destroy(data_set=f"{base_jail_dataset}")

    def base_jail_incomplete(self, distribution: Distribution):
        base_jail_dataset = self.get_base_jail_data_set(distribution)
        return not self.base_jail_exists(distribution) and len(self.ZFS_FACTORY.zfs_list(base_jail_dataset))

    def get_base_jail_data_set(self, distribution) -> str:
        return f"{self._zfs_root_data_set}/{distribution.version}_{distribution.architecture.value}"

    def get_jail_data_set(self, jail_name: str) -> str:
        return f"{self._zfs_root_data_set}/{jail_name}"

    def get_origin_from_jail(self, jail_name: str) -> str:
        jail_data_set = self.get_jail_data_set(jail_name)

        origin_list = self.ZFS_FACTORY.zfs_get(jail_data_set, properties=['origin'])
        origin = origin_list[jail_data_set]['origin']
        components = ['base']
        for component in origin.split('@')[1].replace(self.SNAPSHOT_NAME, '').split('_'):
            if component:
                components.append(component)
        origin = origin.split('@')[0]
        origin = origin.replace(f"{self._zfs_root_data_set}/", "") + ' (' + ','.join(components) + ')'
        return origin
