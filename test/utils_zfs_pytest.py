import platform

import pytest

from test.globals import TEST_DATA_SET, MockingZFS
from jmanager.utils.zfs import ZFSError, ZFSProperty, ZFS, ZFSType


def pytest_generate_tests(metafunc):
    idlist = ['linux']
    argnames = ['zfs']
    argvalues = [([MockingZFS()])]

    if platform.system() == "FreeBSD":
        idlist.append('FreeBSD')
        argvalues.append(([ZFS()]))

    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


class TestZFS:

    def test_zfs_cmd(self, zfs: ZFS):
        zfs.zfs_cmd(cmd="list", arguments=[], options={}, data_set=TEST_DATA_SET)
        assert True

    def test_zfs_error(self, zfs: ZFS):
        with pytest.raises(ZFSError):
            zfs.zfs_cmd(cmd='error', arguments=[], options={}, data_set='zroot')

    def test_zfs_cmd_with_options(self, zfs: ZFS):
        zfs.zfs_create(options={'canmount': 'on'}, data_set=f"{TEST_DATA_SET}/test")
        zfs.zfs_destroy(arguments=[], data_set=f"{TEST_DATA_SET}/test")

    def test_zfs_list_missing_data_set(self, zfs: ZFS):
        data_sets = zfs.zfs_list(data_set=f"{TEST_DATA_SET}/missing_data_set")
        assert len(data_sets) == 0

    def test_zfs_list_without_options(self, zfs: ZFS):
        output = zfs.zfs_list(data_set=TEST_DATA_SET)

        for data_set in output:
            assert ZFSProperty.NAME in data_set and data_set[ZFSProperty.NAME] == TEST_DATA_SET
            assert ZFSProperty.USED in data_set and ZFSProperty.AVAIL in data_set and ZFSProperty.REFER in data_set
            assert ZFSProperty.MOUNTPOINT in data_set and data_set[ZFSProperty.MOUNTPOINT] == f"/{TEST_DATA_SET}"

    def test_zfs_list_depth_option(self, zfs: ZFS):
        zfs.zfs_create(options={}, data_set=f"{TEST_DATA_SET}/test/with/multiple/levels/more/than/one")
        try:
            output = zfs.zfs_list(data_set=TEST_DATA_SET, depth=1)
            depth_one_output = len(output)
            assert len(output) > 1

            output = zfs.zfs_list(data_set=TEST_DATA_SET, depth=-1)
            assert len(output) > depth_one_output
        finally:
            zfs.zfs_destroy(arguments=['-r'], data_set=f"{TEST_DATA_SET}/test")

    def test_zfs_list_properties(self, zfs: ZFS):
        data_sets = zfs.zfs_list(data_set=TEST_DATA_SET, properties=[ZFSProperty.NAME, ZFSProperty.MOUNTPOINT])

        assert len(data_sets[0].keys()) == 2

    def test_zfs_list_types(self, zfs: ZFS):
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

    def test_zfs_snapshot_recursive(self, zfs: ZFS):
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

    def test_zfs_clone_from_dataset(self, zfs: ZFS):
        with pytest.raises(ZFSError):
            zfs.zfs_clone(snapshot=f"{TEST_DATA_SET}", data_set=f"{TEST_DATA_SET}/clone", options={})

    def test_zfs_clone_from_snapshot(self, zfs: ZFS):
        snapshot_name = "clone_snap"
        zfs.zfs_snapshot(data_set=TEST_DATA_SET, snapshot_name=snapshot_name)

        try:
            zfs.zfs_clone(snapshot=f"{TEST_DATA_SET}@{snapshot_name}", data_set=f"{TEST_DATA_SET}/clone", options={})
        finally:
            if zfs.zfs_list(data_set=f"{TEST_DATA_SET}/clone"):
                zfs.zfs_destroy(data_set=f"{TEST_DATA_SET}/clone")
            zfs.zfs_destroy(data_set=f"{TEST_DATA_SET}@{snapshot_name}")

    def test_zfs_get_no_arguments(self, zfs: ZFS):
        data_set_name = f"{TEST_DATA_SET}/test_options"
        options = {
            "mountpoint": "/tmp/test",
            "canmount": "off"
        }
        zfs.zfs_create(data_set=data_set_name, options=options)

        try:
            gathered_options = zfs.zfs_get(data_set=data_set_name)

            for option, value in options.items():
                assert gathered_options[data_set_name][option] == value
        finally:
            zfs.zfs_destroy(data_set=data_set_name)

    def test_zfs_get_recursive_and_depth(self, zfs: ZFS):
        data_set_name = f"{TEST_DATA_SET}/test_options"
        options = {
            "mountpoint": "/tmp/test",
            "canmount": "off"
        }
        zfs.zfs_create(data_set=data_set_name, options=options)
        zfs.zfs_create(data_set=f"{data_set_name}/child", options=options)
        try:
            gathered_options = zfs.zfs_get(data_set=data_set_name, depth=-1)
            assert len(gathered_options) == 2
            gathered_options = zfs.zfs_get(data_set=data_set_name, depth=1)
            assert len(gathered_options) == 2
        finally:
            zfs.zfs_destroy(data_set=data_set_name, arguments=['-R'])

    def test_zfs_get_list_of_properties(self, zfs: ZFS):
        data_set_name = f"{TEST_DATA_SET}/test_options"
        options = {
            "mountpoint": "/tmp/test",
            "canmount": "off"
        }
        zfs.zfs_create(data_set=data_set_name, options=options)

        try:
            gathered_options = zfs.zfs_get(data_set=data_set_name, properties=['mountpoint'])

            assert len(gathered_options[data_set_name]) == 1
        finally:
            zfs.zfs_destroy(data_set=data_set_name)
