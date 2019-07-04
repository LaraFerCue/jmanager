from pathlib import PosixPath
from tarfile import TarFile
from tempfile import TemporaryDirectory

import pytest

from models.distribution import Distribution, Version, VersionType, Architecture
from src.factories.jail_factory import JailFactory
from src.test.globals import MockingZFS

TMP_PATH = PosixPath('/tmp')


class MockingJailFactory(JailFactory):
    ZFS_FACTORY = MockingZFS()


def create_dummy_tarball_in_folder(path_to_folder: PosixPath):
    with TarFile(name=path_to_folder.joinpath('base.txz').as_posix(), mode='w') as tarfile:
        tarfile.add('.', recursive=True)


class TestUtilsJail:
    def test_create_base_data_set_without_tarballs(self):
        jail_factory = MockingJailFactory(TMP_PATH)
        distribution = Distribution(version=Version(12, 0, VersionType.RELEASE), architecture=Architecture.AMD64,
                                    components=[])

        with TemporaryDirectory() as temp_dir:
            with pytest.raises(FileNotFoundError, match=r"Component 'base' not found in"):
                jail_factory.create_base_jail(distribution, PosixPath(temp_dir))

    def test_create_base_data_set(self):
        jail_factory = MockingJailFactory(TMP_PATH)
        distribution = Distribution(version=Version(12, 0, VersionType.RELEASE), architecture=Architecture.AMD64,
                                    components=[])

        with TemporaryDirectory() as temp_dir:
            create_dummy_tarball_in_folder(PosixPath(temp_dir))
            try:
                jail_factory.create_base_jail(distribution=distribution, path_to_tarballs=PosixPath(temp_dir))
            finally:
                pass
