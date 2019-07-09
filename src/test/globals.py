import os
import tarfile
from pathlib import PosixPath

from models.distribution import Distribution, Version, VersionType, Architecture
from src.factories.jail_factory import JailFactory
from src.utils.zfs import ZFS

TEST_DATA_SET = 'zroot/jmanager_test'


class MockingZFS(ZFS):
    ZFS_CMD = "sh scripts/zfs.sh"


RESOURCES_PATH = PosixPath('src/test/resources')
TEST_DISTRIBUTION = Distribution(version=Version(12, 0, VersionType.RELEASE), architecture=Architecture.AMD64,
                                 components=[])


class MockingJailFactory(JailFactory):
    ZFS_FACTORY = MockingZFS()
    JAIL_CMD = "sh scripts/jail.sh"


def create_dummy_tarball_in_folder(path_to_folder: PosixPath):
    os.makedirs(path_to_folder.as_posix(), exist_ok=True)
    with tarfile.open(name=path_to_folder.joinpath('base.txz').as_posix(), mode='w|xz') as tar_file:
        tar_file.add('.', recursive=True)
