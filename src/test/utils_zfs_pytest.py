import pytest

from src.utils.zfs import ZFSError, ZFSProperty, ZFS

TEST_DATA_SET = 'zroot/jmanager_test'


class MockingZFS(ZFS):
    ZFS_CMD = "sh scripts/zfs.sh"


class TestZFS:
    def test_zfs_cmd(self):
        zfs = MockingZFS()
        zfs.zfs_cmd(cmd="list", arguments=[], options={}, data_set='zroot')
        assert True

    def test_zfs_error(self):
        zfs = MockingZFS()
        with pytest.raises(ZFSError):
            zfs.zfs_cmd(cmd='error', arguments=[], options={}, data_set='zroot')

    def test_zfs_cmd_with_options(self):
        zfs = MockingZFS()
        zfs.zfs_cmd(cmd="create", arguments=["-u"], options={'canmount': 'on'}, data_set=f"{TEST_DATA_SET}/test")
        zfs.zfs_cmd(cmd="destroy", arguments=[], options={}, data_set=f"{TEST_DATA_SET}/test")

    def test_zfs_list_without_options(self):
        zfs = MockingZFS()
        output = zfs.zfs_list(data_set=TEST_DATA_SET)

        for data_set in output:
            assert ZFSProperty.NAME in data_set and data_set[ZFSProperty.NAME] == TEST_DATA_SET
            assert ZFSProperty.USED in data_set and ZFSProperty.AVAIL in data_set and ZFSProperty.REFER in data_set
            assert ZFSProperty.MOUNTPOINT in data_set and data_set[ZFSProperty.MOUNTPOINT] == f"/{TEST_DATA_SET}"

    def test_zfs_list_depth_option(self):
        zfs = MockingZFS()
        zfs.zfs_cmd(cmd="create", arguments=["-p"], options={},
                    data_set=f"{TEST_DATA_SET}/test/with/multiple/levels/more/than/one")
        try:
            output = zfs.zfs_list(data_set=TEST_DATA_SET, depth=1)
            depth_one_output = len(output)
            assert len(output) > 1

            output = zfs.zfs_list(data_set=TEST_DATA_SET, depth=-1)
            assert len(output) > depth_one_output
        finally:
            zfs.zfs_cmd(cmd='destroy', arguments=['-r'], options={}, data_set=f"{TEST_DATA_SET}/test")

    def test_zfs_list_properties(self):
        zfs = MockingZFS()
        data_sets = zfs.zfs_list(data_set=TEST_DATA_SET, properties=[ZFSProperty.NAME, ZFSProperty.MOUNTPOINT])

        assert len(data_sets[0].keys()) == 2
