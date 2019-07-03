import pytest

from src.utils.zfs import zfs_cmd, ZFSError, zfs_list, ZFSProperty

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

    def test_zfs_list_without_options(self):
        output = zfs_list(data_set='zroot')

        for data_set in output:
            assert ZFSProperty.NAME in data_set and data_set[ZFSProperty.NAME] == 'zroot'
            assert ZFSProperty.USED in data_set and ZFSProperty.AVAIL in data_set and ZFSProperty.REFER in data_set
            assert ZFSProperty.MOUNTPOINT in data_set and data_set[ZFSProperty.MOUNTPOINT] == '/zroot'
