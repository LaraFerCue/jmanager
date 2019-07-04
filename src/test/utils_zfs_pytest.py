import platform

import pytest

from src.test.globals import TEST_DATA_SET, MockingZFS
from src.utils.zfs import ZFSError, ZFSProperty, ZFS, ZFSType


def pytest_generate_tests(metafunc):
    idlist = ['linux']
    argnames = ['zfs']
    argvalues = [([MockingZFS()])]

    if platform.system() == "FreeBSD":
        idlist.append('FreeBSD')
        argvalues.append(([ZFS()]))

    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


class TestZFS:

    def test_zfs_cmd(self, zfs):
        zfs.zfs_cmd(cmd="list", arguments=[], options={}, data_set=TEST_DATA_SET)
        assert True

    def test_zfs_error(self, zfs):
        with pytest.raises(ZFSError):
            zfs.zfs_cmd(cmd='error', arguments=[], options={}, data_set='zroot')

    def test_zfs_cmd_with_options(self, zfs):
        zfs.zfs_create(options={'canmount': 'on'}, data_set=f"{TEST_DATA_SET}/test")
        zfs.zfs_destroy(arguments=[], data_set=f"{TEST_DATA_SET}/test")

    def test_zfs_list_missing_data_set(self, zfs):
        data_sets = zfs.zfs_list(data_set=f"{TEST_DATA_SET}/missing_data_set")
        assert len(data_sets) == 0

    def test_zfs_list_without_options(self, zfs):
        output = zfs.zfs_list(data_set=TEST_DATA_SET)

        for data_set in output:
            assert ZFSProperty.NAME in data_set and data_set[ZFSProperty.NAME] == TEST_DATA_SET
            assert ZFSProperty.USED in data_set and ZFSProperty.AVAIL in data_set and ZFSProperty.REFER in data_set
            assert ZFSProperty.MOUNTPOINT in data_set and data_set[ZFSProperty.MOUNTPOINT] == f"/{TEST_DATA_SET}"

    def test_zfs_list_depth_option(self, zfs):
        zfs.zfs_create(options={}, data_set=f"{TEST_DATA_SET}/test/with/multiple/levels/more/than/one")
        try:
            output = zfs.zfs_list(data_set=TEST_DATA_SET, depth=1)
            depth_one_output = len(output)
            assert len(output) > 1

            output = zfs.zfs_list(data_set=TEST_DATA_SET, depth=-1)
            assert len(output) > depth_one_output
        finally:
            zfs.zfs_destroy(arguments=['-r'], data_set=f"{TEST_DATA_SET}/test")

    def test_zfs_list_properties(self, zfs):
        data_sets = zfs.zfs_list(data_set=TEST_DATA_SET, properties=[ZFSProperty.NAME, ZFSProperty.MOUNTPOINT])

        assert len(data_sets[0].keys()) == 2

    def test_zfs_list_types(self, zfs):
        snapshot_name = f"{TEST_DATA_SET}@pytest_test"
        zfs.zfs_snapshot(data_set=TEST_DATA_SET, snapshot_name="pytest_test")

        try:
            output = zfs.zfs_list(data_set=TEST_DATA_SET, depth=-1, types=[ZFSType.SNAPSHOT])
            assert len(output) == 1
            assert output[0][ZFSProperty.NAME] == snapshot_name

            output = zfs.zfs_list(data_set=TEST_DATA_SET, depth=-1, types=[ZFSType.FILESYSTEM])
            for data_set in output:
                assert data_set[ZFSProperty.NAME] != snapshot_name

            output = zfs.zfs_list(data_set=TEST_DATA_SET, depth=-1, types=[ZFSType.FILESYSTEM, ZFSType.SNAPSHOT])
            data_set_names = [x[ZFSProperty.NAME] for x in output]
            assert snapshot_name in data_set_names
            assert TEST_DATA_SET in data_set_names

        finally:
            zfs.zfs_destroy(arguments=[], data_set=snapshot_name)

    def test_zfs_snapshot_recursive(self, zfs):
        data_set_path = "a/lot/of/nested/datasets"
        zfs.zfs_create(data_set=f"{TEST_DATA_SET}/{data_set_path}", options={})

        try:
            zfs.zfs_snapshot(data_set=f"{TEST_DATA_SET}/a", snapshot_name="pytest_test", recursive=True)

            snapshots_names = [
                f'{TEST_DATA_SET}/a@pytest_test',
                f'{TEST_DATA_SET}/a/lot@pytest_test',
                f'{TEST_DATA_SET}/a/lot/of@pytest_test',
                f'{TEST_DATA_SET}/a/lot/of/nested@pytest_test',
                f'{TEST_DATA_SET}/a/lot/of/nested/datasets@pytest_test',
            ]
            snapshots = [snap[ZFSProperty.NAME] for snap in zfs.zfs_list(data_set=f"{TEST_DATA_SET}/a", depth=-1,
                                                                         types=[ZFSType.SNAPSHOT],
                                                                         properties=[ZFSProperty.NAME])]

            for dataset in snapshots_names:
                assert dataset in snapshots

        finally:
            zfs.zfs_destroy(data_set=f"{TEST_DATA_SET}/a", arguments=['-R'])
