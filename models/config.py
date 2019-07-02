from pathlib import PosixPath
from typing import Dict


class Config:
    def __init__(self, zfs_pool: str, jail_base_path: str, user: str):
        self._zfs_pool = zfs_pool
        self._jail_base_path = PosixPath(jail_base_path)
        self._user = user

    @property
    def zfs_pool(self) -> str:
        return self._zfs_pool

    @property
    def jail_base_path(self) -> PosixPath:
        return self._jail_base_path

    @property
    def user(self) -> str:
        return self._user

    @staticmethod
    def from_dictionary(config_dict: Dict[str, str]):
        for key in config_dict:
            if not isinstance(config_dict[key], str):
                raise ValueError(f"{key} must be of type 'str' found '{type(config_dict[key]).__name__}'")
        return Config(**config_dict)
