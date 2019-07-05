from pathlib import PosixPath

from src.utils.zfs import ZFS

TEST_DATA_SET = 'zroot/jmanager_test'


class MockingZFS(ZFS):
    ZFS_CMD = "sh scripts/zfs.sh"


RESOURCES_PATH = PosixPath('src/test/resources')