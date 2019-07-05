import shutil
from pathlib import PosixPath
from tarfile import TarFile
from tempfile import TemporaryDirectory

import pytest

from src.factories.jail_factory import JailFactory
from src.test.globals import MockingZFS, TEST_DATA_SET, TEST_DISTRIBUTION

TMP_PATH = PosixPath('/tmp').joinpath('jmanager')


class MockingJailFactory(JailFactory):
    ZFS_FACTORY = MockingZFS()


def create_dummy_tarball_in_folder(path_to_folder: PosixPath):
    with TarFile(name=path_to_folder.joinpath('base.txz').as_posix(), mode='w') as tarfile:
        tarfile.add('.', recursive=True)


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
        assert not jail_factory.jail_exists(distribution)

        jail_path = f"{distribution.version}_{distribution.architecture.value}"
        jail_factory.ZFS_FACTORY.zfs_create(f"{TEST_DATA_SET}/{jail_path}", options={})
        jail_exists = jail_factory.jail_exists(distribution)
        jail_factory.ZFS_FACTORY.zfs_destroy(f"{TEST_DATA_SET}/{jail_path}")
        assert jail_exists

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
                assert jail_factory.jail_exists(distribution=distribution)
                assert PosixPath(temp_dir).joinpath(
                    f"{distribution.version}_{distribution.architecture.value}").iterdir()
            finally:
                jail_factory.ZFS_FACTORY.zfs_destroy(
                    f"{TEST_DATA_SET}/{distribution.version}_{distribution.architecture.value}")

    # def test_create_jail_without_options(self):
    #     jail_name = "test_no_options"
    #     jail_info = Jail(name=jail_name)
    #     jail_factory = MockingJailFactory(jail_root_path=TMP_PATH,
    #                                       zfs_root_data_set=TEST_DATA_SET,
    #                                       jail_config_folder=TMP_PATH)
    #     jail_factory.ZFS_FACTORY.zfs_create(data_set=f"{TEST_DATA_SET}")
    #     jail_factory.create_jail(jail_data=jail_info, os_version=Version(12, 0, VersionType.RELEASE),
    #                              architecture=Architecture.AMD64)
    #     loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(f"{jail_name}.conf"))
    #     assert loaded_jail.name == jail_name
