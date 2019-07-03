import pytest

from src.utils.zfs import zfs_cmd, ZFSError

TEST_DATA_SET = 'zroot/jmanager_test/test'


class TestZFS:
    def test_zfs_cmd(self):
        zfs_cmd(cmd="list", arguments=[], options={}, data_set='zroot')
        assert True

    def test_zfs_error(self):
        with pytest.raises(ZFSError):
            zfs_cmd(cmd='error', arguments=[], options={}, data_set='zroot')

    def test_zfs_cmd_with_options(self):
        zfs_cmd(cmd="create", arguments=["-u"], options={'canmount': 'on'}, data_set=TEST_DATA_SET)
        zfs_cmd(cmd="destroy", arguments=[], options={}, data_set=TEST_DATA_SET)
