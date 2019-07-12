import os
import shutil
import tarfile
from pathlib import PosixPath

from models.distribution import Distribution, Version, VersionType, Architecture
from src.factories.base_jail_factory import BaseJailFactory
from src.factories.data_set_factory import DataSetFactory
from src.factories.jail_factory import JailFactory
from src.utils.zfs import ZFS

TMP_PATH = PosixPath('/tmp').joinpath('jmanager_test')
TEST_DATA_SET = 'zroot/jmanager_test'
RESOURCES_PATH = PosixPath('src/test/resources')
TEST_DISTRIBUTION = Distribution(version=Version(12, 0, VersionType.RELEASE), architecture=Architecture.AMD64,
                                 components=[])
DUMMY_BASE_JAIL_DATA_SET = f"{TEST_DATA_SET}/{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}"


class MockingZFS(ZFS):
    ZFS_CLI = "sh scripts/zfs.sh"


class MockingJailFactory(JailFactory):
    JAIL_CMD = "sh scripts/jail.sh"


class MockingDataSetFactory(DataSetFactory):
    ZFS_FACTORY = MockingZFS()


class MockingBaseJailFactory(BaseJailFactory):
    JAIL_CMD = "sh scripts/jail.sh"


def create_dummy_tarball_in_folder(path_to_folder: PosixPath):
    os.makedirs(path_to_folder.as_posix(), exist_ok=True)
    with tarfile.open(name=path_to_folder.joinpath('base.txz').as_posix(), mode='w|xz') as tar_file:
        tar_file.add('models', recursive=True)
    with tarfile.open(name=path_to_folder.joinpath('src.txz').as_posix(), mode='w|xz') as tar_file:
        tar_file.add('src', recursive=True)
    with tarfile.open(name=path_to_folder.joinpath('lib32.txz').as_posix(), mode='w|xz') as tar_file:
        tar_file.add('examples', recursive=True)


def get_mocking_base_jail_factory(temp_dir: PosixPath) -> MockingBaseJailFactory:
    data_set_factory = MockingDataSetFactory(zfs_root_data_set=TEST_DATA_SET)
    return MockingBaseJailFactory(jail_root_path=temp_dir, data_set_factory=data_set_factory)


def get_mocking_jail_factory() -> MockingJailFactory:
    base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
    jail_factory = MockingJailFactory(base_jail_factory=base_jail_factory,
                                      jail_config_folder=TMP_PATH)
    return jail_factory


def create_dummy_base_jail(distribution: Distribution = TEST_DISTRIBUTION):
    zfs = MockingZFS()
    data_set = f"{TEST_DATA_SET}/{distribution.version}_{distribution.architecture.value}"

    if len(zfs.zfs_list(data_set=data_set)) < 1:
        zfs.zfs_create(data_set=data_set, options={})
    zfs.zfs_snapshot(data_set=data_set, snapshot_name=get_dummy_snapshot_name(distribution))


def get_dummy_snapshot_name(distribution):
    base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
    snapshot_name = base_jail_factory.get_snapshot_name(component_list=distribution.components)
    return snapshot_name


def destroy_dummy_base_jail(distribution: Distribution = TEST_DISTRIBUTION):
    zfs = MockingZFS()
    data_set = get_dummy_data_set(distribution)
    zfs.zfs_destroy(data_set=data_set, arguments=['-R'])


def get_dummy_data_set(distribution):
    return f"{TEST_DATA_SET}/{distribution.version}_{distribution.architecture.value}"


def destroy_dummy_jail(jail_name: str):
    zfs = MockingZFS()
    shutil.rmtree(TMP_PATH.joinpath(jail_name), ignore_errors=True)
    zfs.zfs_destroy(data_set=f"{TEST_DATA_SET}/{jail_name}")


def remove_path(temp_dir: PosixPath = TMP_PATH):
    if temp_dir.exists():
        if temp_dir.is_dir():
            shutil.rmtree(temp_dir.as_posix())
        else:
            temp_dir.unlink()