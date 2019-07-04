import pytest

from src.utils.zfs import zfs_cmd, ZFSError, zfs_list, ZFSProperty

TEST_DATA_SET = 'zroot/jmanager_test'


class TestZFS:
    def test_zfs_cmd(self):
        zfs_cmd(cmd="list", arguments=[], options={}, data_set='zroot')
        assert True

    def test_zfs_error(self):
        with pytest.raises(ZFSError):
            zfs_cmd(cmd='error', arguments=[], options={}, data_set='zroot')

    def test_zfs_cmd_with_options(self):
        zfs_cmd(cmd="create", arguments=["-u"], options={'canmount': 'on'}, data_set=f"{TEST_DATA_SET}/test")
        zfs_cmd(cmd="destroy", arguments=[], options={}, data_set=f"{TEST_DATA_SET}/test")

    def test_zfs_list_without_options(self):
        output = zfs_list(data_set=TEST_DATA_SET)

        for data_set in output:
            assert ZFSProperty.NAME in data_set and data_set[ZFSProperty.NAME] == TEST_DATA_SET
            assert ZFSProperty.USED in data_set and ZFSProperty.AVAIL in data_set and ZFSProperty.REFER in data_set
            assert ZFSProperty.MOUNTPOINT in data_set and data_set[ZFSProperty.MOUNTPOINT] == f"/{TEST_DATA_SET}"

    def test_zfs_list_depth_option(self):
        zfs_cmd(cmd="create", arguments=["-p"], options={},
                data_set=f"{TEST_DATA_SET}/test/with/multiple/levels/more/than/one")
        output = zfs_list(data_set=TEST_DATA_SET, depth=1)
        depth_one_output = len(output)
        assert len(output) > 1

        output = zfs_list(data_set=TEST_DATA_SET, depth=-1)
        assert len(output) > depth_one_output
