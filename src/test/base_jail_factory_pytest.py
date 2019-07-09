import shutil
from pathlib import PosixPath
from tempfile import TemporaryDirectory

import pytest

from models.jail import JailError
from src.test.globals import TEST_DISTRIBUTION, TEST_DATA_SET, create_dummy_tarball_in_folder, \
    get_mocking_base_jail_factory, TMP_PATH, create_dummy_base_jail, DUMMY_BASE_JAIL_DATA_SET, destroy_dummy_base_jail


class TestBaseJailFactory:
    def test_jail_factory_jail_path_do_not_exist(self):
        if TMP_PATH.exists():
            shutil.rmtree(TMP_PATH.as_posix())
        get_mocking_base_jail_factory(TMP_PATH)
        assert TMP_PATH.is_dir()

    def test_jail_factory_jail_path_is_a_file(self):
        if TMP_PATH.exists():
            shutil.rmtree(TMP_PATH.as_posix(), ignore_errors=True)
        open(TMP_PATH.as_posix(), 'w').close()

        with pytest.raises(PermissionError, match=r"The jail root path exists and it is not a directory"):
            get_mocking_base_jail_factory(TMP_PATH)
        TMP_PATH.unlink()

    def test_exists_base_jail(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        assert not base_jail_factory.base_jail_exists(distribution=TEST_DISTRIBUTION)

        jail_path = f"{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}"
        base_jail_factory.ZFS_FACTORY.zfs_create(f"{TEST_DATA_SET}/{jail_path}", options={})
        base_jail_factory.ZFS_FACTORY.zfs_create(f"{TEST_DATA_SET}/{jail_path}@{base_jail_factory.SNAPSHOT_NAME}",
                                                 options={})
        jail_exists = base_jail_factory.base_jail_exists(TEST_DISTRIBUTION)
        base_jail_factory.ZFS_FACTORY.zfs_destroy(f"{TEST_DATA_SET}/{jail_path}@{base_jail_factory.SNAPSHOT_NAME}")
        base_jail_factory.ZFS_FACTORY.zfs_destroy(f"{TEST_DATA_SET}/{jail_path}")
        assert jail_exists

    def test_base_jail_incomplete(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        jail_path = f"{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}"

        try:
            base_jail_factory.ZFS_FACTORY.zfs_create(f"{TEST_DATA_SET}/{jail_path}", options={})
            assert base_jail_factory.base_jail_incomplete(distribution=TEST_DISTRIBUTION)

            base_jail_factory.ZFS_FACTORY.zfs_create(f"{TEST_DATA_SET}/{jail_path}@{base_jail_factory.SNAPSHOT_NAME}",
                                                     options={})
            assert not base_jail_factory.base_jail_incomplete(distribution=TEST_DISTRIBUTION)
        finally:
            if base_jail_factory.base_jail_exists(distribution=TEST_DISTRIBUTION):
                base_jail_factory.ZFS_FACTORY.zfs_destroy(
                    f"{TEST_DATA_SET}/{jail_path}@{base_jail_factory.SNAPSHOT_NAME}")
            base_jail_factory.ZFS_FACTORY.zfs_destroy(f"{TEST_DATA_SET}/{jail_path}")

    def test_destroy_base_jail(self):
        dataset_name = f"{TEST_DATA_SET}/{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}"
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        base_jail_factory.ZFS_FACTORY.zfs_create(data_set=dataset_name, options={})
        base_jail_factory.ZFS_FACTORY.zfs_create(data_set=f"{dataset_name}@{base_jail_factory.SNAPSHOT_NAME}",
                                                 options={})

        base_jail_factory.destroy_base_jail(TEST_DISTRIBUTION)
        assert not base_jail_factory.base_jail_incomplete(TEST_DISTRIBUTION)
        assert not base_jail_factory.base_jail_exists(distribution=TEST_DISTRIBUTION)

    def test_create_base_data_set_without_tarballs(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        with TemporaryDirectory() as temp_dir:
            with pytest.raises(FileNotFoundError, match=r"Component 'base' not found in"):
                base_jail_factory.create_base_jail(TEST_DISTRIBUTION, PosixPath(temp_dir))

    def test_create_base_data_set(self):
        with TemporaryDirectory() as temp_dir:
            base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
            create_dummy_tarball_in_folder(PosixPath(temp_dir))
            try:
                base_jail_factory.create_base_jail(distribution=TEST_DISTRIBUTION,
                                                   path_to_tarballs=PosixPath(temp_dir))
                assert base_jail_factory.base_jail_exists(distribution=TEST_DISTRIBUTION)
                assert PosixPath(temp_dir).joinpath(
                    f"{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}").iterdir()
            finally:
                base_jail_factory.destroy_base_jail(distribution=TEST_DISTRIBUTION)

    def test_create_duplicated_base_jail(self):
        with TemporaryDirectory() as temp_dir:
            base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
            create_dummy_tarball_in_folder(PosixPath(temp_dir))
            try:
                base_jail_factory.create_base_jail(distribution=TEST_DISTRIBUTION,
                                                   path_to_tarballs=PosixPath(temp_dir))
                with pytest.raises(JailError, match=r"The base jail for '12.0-RELEASE/amd64' exists"):
                    base_jail_factory.create_base_jail(distribution=TEST_DISTRIBUTION,
                                                       path_to_tarballs=PosixPath(temp_dir))

                dataset = f"{TEST_DATA_SET}/{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}" + \
                          f"@{base_jail_factory.SNAPSHOT_NAME}"
                base_jail_factory.ZFS_FACTORY.zfs_destroy(data_set=dataset)
                incomplete_base_jail_msg = r"The base jail '12.0-RELEASE/amd64' has left overs, " + \
                                           "delete them and try again."
                with pytest.raises(JailError, match=incomplete_base_jail_msg):
                    base_jail_factory.create_base_jail(distribution=TEST_DISTRIBUTION,
                                                       path_to_tarballs=PosixPath(temp_dir))
            finally:
                base_jail_factory.destroy_base_jail(distribution=TEST_DISTRIBUTION)

    def test_get_origin_from_jail(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        create_dummy_base_jail()
        try:
            base_jail_factory.ZFS_FACTORY.zfs_clone(
                snapshot=f"{DUMMY_BASE_JAIL_DATA_SET}@{base_jail_factory.SNAPSHOT_NAME}",
                data_set=f"{TEST_DATA_SET}/test",
                options={}
            )
            assert base_jail_factory.get_origin_from_jail('test') == "12.0-RELEASE_amd64"
        finally:
            base_jail_factory.ZFS_FACTORY.zfs_destroy(f"{TEST_DATA_SET}/test")
            destroy_dummy_base_jail()
