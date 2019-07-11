from pathlib import PosixPath
from tempfile import TemporaryDirectory

import pytest

from models.distribution import Distribution, Component
from models.jail import JailError
from src.test.globals import get_mocking_base_jail_factory, TMP_PATH, TEST_DISTRIBUTION, create_dummy_tarball_in_folder, \
    destroy_dummy_base_jail


class TestBaseJailFactoryCreate:
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

    def test_create_base_data_set_with_multiple_components(self):
        distribution = Distribution(version=TEST_DISTRIBUTION.version,
                                    architecture=TEST_DISTRIBUTION.architecture,
                                    components=[Component.SRC, Component.LIB32])
        lib32_distribution = Distribution(version=TEST_DISTRIBUTION.version,
                                          architecture=TEST_DISTRIBUTION.architecture,
                                          components=[Component.LIB32])
        with TemporaryDirectory() as temp_dir:
            base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
            create_dummy_tarball_in_folder(PosixPath(temp_dir))
            try:
                base_jail_factory.create_base_jail(distribution=distribution,
                                                   path_to_tarballs=PosixPath(temp_dir))
                assert base_jail_factory.base_jail_exists(distribution=distribution)
                assert base_jail_factory.base_jail_exists(distribution=lib32_distribution)
                assert base_jail_factory.base_jail_exists(distribution=TEST_DISTRIBUTION)
                assert PosixPath(temp_dir).joinpath(
                    f"{TEST_DISTRIBUTION.version}_{TEST_DISTRIBUTION.architecture.value}").iterdir()
            finally:
                destroy_dummy_base_jail(distribution=TEST_DISTRIBUTION)

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
            finally:
                base_jail_factory.destroy_base_jail(distribution=TEST_DISTRIBUTION)

    def test_create_accumulative_base_jails(self):
        distribution = Distribution(
            version=TEST_DISTRIBUTION.version, architecture=TEST_DISTRIBUTION.architecture,
            components=[Component.LIB32]
        )
        with TemporaryDirectory() as temp_dir:
            base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
            create_dummy_tarball_in_folder(PosixPath(temp_dir))
            try:
                base_jail_factory.create_base_jail(distribution=TEST_DISTRIBUTION,
                                                   path_to_tarballs=PosixPath(temp_dir))
                base_jail_factory.create_base_jail(distribution=distribution,
                                                   path_to_tarballs=PosixPath(temp_dir))
                jails = base_jail_factory.list_base_jails()
                assert len(jails) == 2
            finally:
                destroy_dummy_base_jail(TEST_DISTRIBUTION)

    def test_create_callback(self):
        def _callback(msg, iteration, total):
            assert msg == "Extracting base.txz"
            assert isinstance(iteration, int)
            assert isinstance(total, int)
            assert iteration < total

        with TemporaryDirectory() as temp_dir:
            base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
            create_dummy_tarball_in_folder(PosixPath(temp_dir))
            try:
                base_jail_factory.create_base_jail(distribution=TEST_DISTRIBUTION,
                                                   path_to_tarballs=PosixPath(temp_dir),
                                                   callback=_callback)
            finally:
                destroy_dummy_base_jail(TEST_DISTRIBUTION)
