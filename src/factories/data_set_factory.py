from pathlib import PosixPath
from typing import List, Dict

from jmanager.utils.zfs import ZFS, ZFSProperty, ZFSType


class DataSetFactory:
    ZFS_FACTORY = ZFS()

    def __init__(self, zfs_root_data_set: str):
        self._zfs_root_data_set = zfs_root_data_set

    def get_data_set_path(self, data_set_name: str):
        return f"{self._zfs_root_data_set}/{data_set_name}"

    def base_data_set_exists(self, data_set_name: str):
        data_set = self.get_data_set_path(data_set_name=data_set_name)
        return len(self.ZFS_FACTORY.zfs_list(data_set=data_set))

    def snapshot_exists(self, data_set_name: str, snapshot: str):
        data_set = self.get_data_set_path(data_set_name=data_set_name)
        return len(self.ZFS_FACTORY.zfs_list(f"{data_set}@{snapshot}"))

    def create_snapshot(self, data_set_name: str, snapshot: str):
        data_set = self.get_data_set_path(data_set_name=data_set_name)
        self.ZFS_FACTORY.zfs_snapshot(data_set=data_set, snapshot_name=snapshot)

    def create_base_data_set(self, data_set_name: str, mountpoint: PosixPath):
        data_set = self.get_data_set_path(data_set_name=data_set_name)
        self.ZFS_FACTORY.zfs_create(
            data_set=data_set,
            options={"mountpoint": mountpoint.as_posix(),
                     "dedup": "sha512",
                     "atime": "off"}
        )

    def delete_snapshot(self, data_set_name: str, snapshot_name: str):
        data_set = self.get_data_set_path(data_set_name=data_set_name)
        self.ZFS_FACTORY.zfs_destroy(data_set=f"{data_set}@{snapshot_name}")

    def delete_data_set(self, data_set_name: str):
        data_set = self.get_data_set_path(data_set_name=data_set_name)
        self.ZFS_FACTORY.zfs_destroy(data_set=data_set)

    def list_of_snapshots(self) -> List[str]:
        items = self.ZFS_FACTORY.zfs_list(data_set=self._zfs_root_data_set, depth=-1,
                                          properties=[ZFSProperty.NAME],
                                          types=[ZFSType.SNAPSHOT])
        list_of_snapshots: List[str] = []
        for item in items:
            data_set_name = item[ZFSProperty.NAME].replace(f"{self._zfs_root_data_set}/", '')
            list_of_snapshots.append(data_set_name)
        return list_of_snapshots

    def clone(self, data_set_name: str, snapshot_name: str, clone_data_set_name: str, options: Dict[str, str]):
        self.ZFS_FACTORY.zfs_clone(
            snapshot=f"{self.get_data_set_path(data_set_name=data_set_name)}@{snapshot_name}",
            data_set=self.get_data_set_path(clone_data_set_name),
            options=options
        )

    def __eq__(self, other: 'DataSetFactory') -> bool:
        return self._zfs_root_data_set == other._zfs_root_data_set
