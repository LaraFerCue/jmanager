import shutil
from pathlib import PosixPath
from tempfile import TemporaryDirectory

import pytest

from models.jail import Jail, JailOption
from src.factories.jail_factory import JailError
from src.test.globals import TEST_DATA_SET, TEST_DISTRIBUTION, MockingJailFactory, create_dummy_tarball_in_folder

TMP_PATH = PosixPath('/tmp').joinpath('jmanager')


def create_dummy_base_jail(jail_factory):
    dataset_name = f"{TEST_DATA_SET}/{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}"
    jail_factory.ZFS_FACTORY.zfs_create(data_set=dataset_name, options={})
    jail_factory.ZFS_FACTORY.zfs_snapshot(data_set=dataset_name, snapshot_name=jail_factory.SNAPSHOT_NAME)


class TestJailFactory:
    def test_jail_factory_jail_path_do_not_exist(self):
        MockingJailFactory(jail_root_path=TMP_PATH, zfs_root_data_set=TEST_DATA_SET, jail_config_folder=TMP_PATH)
        assert TMP_PATH.is_dir()

    def test_jail_factory_jail_path_is_a_file(self):
        if TMP_PATH.exists():
            shutil.rmtree(TMP_PATH.as_posix(), ignore_errors=True)
        open(TMP_PATH.as_posix(), 'w').close()

        with pytest.raises(PermissionError, match=r"The jail root path exists and it is not a directory"):
            MockingJailFactory(jail_root_path=TMP_PATH, zfs_root_data_set=TEST_DATA_SET, jail_config_folder=TMP_PATH)
        TMP_PATH.unlink()

    def test_exists_base_jail(self):
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
                                          zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        distribution = TEST_DISTRIBUTION
        assert not jail_factory.base_jail_exists(distribution)

        jail_path = f"{distribution.version}_{distribution.architecture.value}"
        jail_factory.ZFS_FACTORY.zfs_create(f"{TEST_DATA_SET}/{jail_path}", options={})
        jail_factory.ZFS_FACTORY.zfs_create(f"{TEST_DATA_SET}/{jail_path}@{jail_factory.SNAPSHOT_NAME}", options={})
        jail_exists = jail_factory.base_jail_exists(distribution)
        jail_factory.ZFS_FACTORY.zfs_destroy(f"{TEST_DATA_SET}/{jail_path}@{jail_factory.SNAPSHOT_NAME}")
        jail_factory.ZFS_FACTORY.zfs_destroy(f"{TEST_DATA_SET}/{jail_path}")
        assert jail_exists

    def test_base_jail_incomplete(self):
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
                                          zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        distribution = TEST_DISTRIBUTION
        jail_path = f"{distribution.version}_{distribution.architecture.value}"

        try:
            jail_factory.ZFS_FACTORY.zfs_create(f"{TEST_DATA_SET}/{jail_path}", options={})
            assert jail_factory.base_jail_incomplete(distribution=distribution)

            jail_factory.ZFS_FACTORY.zfs_create(f"{TEST_DATA_SET}/{jail_path}@{jail_factory.SNAPSHOT_NAME}", options={})
            assert not jail_factory.base_jail_incomplete(distribution=distribution)
        finally:
            if jail_factory.base_jail_exists(distribution):
                jail_factory.ZFS_FACTORY.zfs_destroy(f"{TEST_DATA_SET}/{jail_path}@{jail_factory.SNAPSHOT_NAME}")
            jail_factory.ZFS_FACTORY.zfs_destroy(f"{TEST_DATA_SET}/{jail_path}")

    def test_destroy_base_jail(self):
        dataset_name = f"{TEST_DATA_SET}/{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}"
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
                                          zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        jail_factory.ZFS_FACTORY.zfs_create(data_set=dataset_name, options={})
        jail_factory.ZFS_FACTORY.zfs_create(data_set=f"{dataset_name}@{jail_factory.SNAPSHOT_NAME}", options={})

        jail_factory.destroy_base_jail(TEST_DISTRIBUTION)
        assert not jail_factory.base_jail_incomplete(TEST_DISTRIBUTION)
        assert not jail_factory.base_jail_exists(TEST_DISTRIBUTION)

    def test_create_base_data_set_without_tarballs(self):
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
                                          zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        distribution = TEST_DISTRIBUTION

        with TemporaryDirectory() as temp_dir:
            with pytest.raises(FileNotFoundError, match=r"Component 'base' not found in"):
                jail_factory.create_base_jail(distribution, PosixPath(temp_dir))

    def test_create_base_data_set(self):
        distribution = TEST_DISTRIBUTION

        with TemporaryDirectory() as temp_dir:
            jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
                                              zfs_root_data_set=TEST_DATA_SET,
                                              jail_config_folder=TMP_PATH)
            create_dummy_tarball_in_folder(PosixPath(temp_dir))
            try:
                jail_factory.create_base_jail(distribution=distribution, path_to_tarballs=PosixPath(temp_dir))
                assert jail_factory.base_jail_exists(distribution=distribution)
                assert PosixPath(temp_dir).joinpath(
                    f"{distribution.version}_{distribution.architecture.value}").iterdir()
            finally:
                jail_factory.destroy_base_jail(distribution=distribution)

    def test_create_duplicated_base_jail(self):
        distribution = TEST_DISTRIBUTION

        with TemporaryDirectory() as temp_dir:
            jail_factory = MockingJailFactory(jail_root_path=PosixPath(temp_dir),
                                              zfs_root_data_set=TEST_DATA_SET,
                                              jail_config_folder=TMP_PATH)
            create_dummy_tarball_in_folder(PosixPath(temp_dir))
            try:
                jail_factory.create_base_jail(distribution=distribution, path_to_tarballs=PosixPath(temp_dir))
                with pytest.raises(JailError, match=r"The base jail for '12.0-RELEASE/amd64' exists"):
                    jail_factory.create_base_jail(distribution=distribution, path_to_tarballs=PosixPath(temp_dir))

                dataset = f"{TEST_DATA_SET}/{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}" + \
                          f"@{jail_factory.SNAPSHOT_NAME}"
                jail_factory.ZFS_FACTORY.zfs_destroy(data_set=dataset)
                incomplete_base_jail_msg = r"The base jail '12.0-RELEASE/amd64' has left overs, " + \
                                           "delete them and try again."
                with pytest.raises(JailError, match=incomplete_base_jail_msg):
                    jail_factory.create_base_jail(distribution=distribution, path_to_tarballs=PosixPath(temp_dir))
            finally:
                jail_factory.destroy_base_jail(distribution=distribution)

    def test_create_jail_without_options(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name)
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
                                          zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        create_dummy_base_jail(jail_factory)

        try:
            jail_factory.create_jail(jail_data=jail_info, os_version=TEST_DISTRIBUTION.version,
                                     architecture=TEST_DISTRIBUTION.architecture)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(f"{jail_name}.conf"))
            assert loaded_jail.name == jail_name
            assert jail_factory.ZFS_FACTORY.zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            for option, value in jail_factory.get_jail_default_options(jail_info, TEST_DISTRIBUTION.version).items():
                assert loaded_jail.options[option] == value
        finally:
            jail_factory.ZFS_FACTORY.zfs_destroy(data_set=f"{TEST_DATA_SET}/{jail_name}")
            jail_factory.destroy_base_jail(distribution=TEST_DISTRIBUTION)
            TMP_PATH.joinpath(f"{jail_name}.conf").unlink()

    def test_create_jail_overriding_default_options(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name, options={JailOption.HOSTNAME: "no host name"})
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
                                          zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        create_dummy_base_jail(jail_factory)

        try:
            jail_factory.create_jail(jail_data=jail_info, os_version=TEST_DISTRIBUTION.version,
                                     architecture=TEST_DISTRIBUTION.architecture)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(f"{jail_name}.conf"))
            assert loaded_jail.name == jail_name
            assert jail_factory.ZFS_FACTORY.zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            assert loaded_jail.options[JailOption.HOSTNAME] == "no host name"
        finally:
            jail_factory.ZFS_FACTORY.zfs_destroy(data_set=f"{TEST_DATA_SET}/{jail_name}")
            jail_factory.destroy_base_jail(distribution=TEST_DISTRIBUTION)
            TMP_PATH.joinpath(f"{jail_name}.conf").unlink()

    def test_create_jail_with_additional_options(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name, options={JailOption.IP4: "new"})
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
                                          zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        create_dummy_base_jail(jail_factory)

        try:
            jail_factory.create_jail(jail_data=jail_info, os_version=TEST_DISTRIBUTION.version,
                                     architecture=TEST_DISTRIBUTION.architecture)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(f"{jail_name}.conf"))
            assert loaded_jail.name == jail_name
            assert jail_factory.ZFS_FACTORY.zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            assert loaded_jail.options[JailOption.IP4] == "new"
        finally:
            jail_factory.ZFS_FACTORY.zfs_destroy(data_set=f"{TEST_DATA_SET}/{jail_name}")
            jail_factory.destroy_base_jail(distribution=TEST_DISTRIBUTION)
            TMP_PATH.joinpath(f"{jail_name}.conf").unlink()

    def test_create_jail_without_base_jail(self):
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH, zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        with pytest.raises(JailError, match=r"The base jail for version 12.0-RELEASE/amd64 does not exist"):
            jail_factory.create_jail(Jail('test'), TEST_DISTRIBUTION.version, TEST_DISTRIBUTION.architecture)

    def test_create_duplicated_jail(self):
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH, zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        create_dummy_base_jail(jail_factory)
        jail_factory.ZFS_FACTORY.zfs_create(data_set=f"{TEST_DATA_SET}/test", options={})

        with open(TMP_PATH.joinpath('test.conf').as_posix(), "w") as fd:
            fd.write("test\n")

        try:
            with pytest.raises(JailError, match=r"The jail 'test' already exists"):
                jail_factory.create_jail(Jail('test'), TEST_DISTRIBUTION.version, TEST_DISTRIBUTION.architecture)

            TMP_PATH.joinpath('test.conf').unlink()
            with pytest.raises(JailError,
                               match=r"The jail 'test' has some left overs, please remove them and try again."):
                jail_factory.create_jail(Jail('test'), TEST_DISTRIBUTION.version, TEST_DISTRIBUTION.architecture)
        finally:
            jail_factory.ZFS_FACTORY.zfs_destroy(data_set=f"{TEST_DATA_SET}/test")
            jail_factory.destroy_base_jail(TEST_DISTRIBUTION)
            if TMP_PATH.joinpath('test.conf').is_file():
                TMP_PATH.joinpath('test.conf').unlink()

    def test_jail_exists(self):
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH, zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        jail_name = "test_jail_exists"
        assert not jail_factory.jail_exists(jail_name)
        open(TMP_PATH.joinpath(f'{jail_name}.conf').as_posix(), 'w').close()

        try:
            assert jail_factory.jail_exists(jail_name)
        finally:
            TMP_PATH.joinpath(f'{jail_name}.conf').unlink()

    def test_destroy_jail(self):
        jail_name = "test_no_options"
        jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
                                          zfs_root_data_set=TEST_DATA_SET,
                                          jail_config_folder=TMP_PATH)
        create_dummy_base_jail(jail_factory)

        try:
            jail_factory.create_jail(jail_data=Jail(jail_name), os_version=TEST_DISTRIBUTION.version,
                                     architecture=TEST_DISTRIBUTION.architecture)
            jail_factory.destroy_jail(jail_name=jail_name)
            assert not TMP_PATH.joinpath(f"{jail_name}.conf").is_file()
            assert not len(jail_factory.ZFS_FACTORY.zfs_list(f"{TEST_DATA_SET}/{jail_name}"))
        finally:
            jail_factory.destroy_base_jail(distribution=TEST_DISTRIBUTION)
