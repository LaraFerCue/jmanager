from pathlib import PosixPath

from models.distribution import Distribution
from models.jail import Jail
from src.utils.zfs import ZFS


class JailFactory:
    ZFS_FACTORY = ZFS()

    def __init__(self, jail_root_path: PosixPath):
        self._jail_root_path = jail_root_path

    def create_base_jail(self, distribution: Distribution, path_to_tarballs: PosixPath):
        for component in distribution.components:
            if not path_to_tarballs.joinpath(f"{component.value}.txz").is_file():
                raise FileNotFoundError(f"Component '{component.value}' not found in {path_to_tarballs}")

    def create_jail(self, jail_data: Jail, distribution: Distribution, path_to_tarballs: PosixPath):
        pass
