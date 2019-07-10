import shutil
from pathlib import PosixPath
from tempfile import TemporaryDirectory

import pytest

from models.distribution import Distribution, Component
from models.jail import JailError
from src.test.globals import TEST_DISTRIBUTION, create_dummy_tarball_in_folder, \
    get_mocking_base_jail_factory, TMP_PATH, create_dummy_base_jail, destroy_dummy_base_jail, \
    destroy_dummy_jail, create_dummy_jail

TEST_JAIL_NAME = "test"


class TestBaseJailFactory:
    def test_get_snapshot_name(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        assert base_jail_factory.get_snapshot_name(TEST_DISTRIBUTION.components) == base_jail_factory.SNAPSHOT_NAME
        distribution = Distribution(
            version=TEST_DISTRIBUTION.version,
            architecture=TEST_DISTRIBUTION.architecture,
            components=[Component.SRC]
        )
        assert base_jail_factory.get_snapshot_name(distribution.components) == f"{base_jail_factory.SNAPSHOT_NAME}_src"
        distribution = Distribution(
            version=TEST_DISTRIBUTION.version,
            architecture=TEST_DISTRIBUTION.architecture,
            components=[Component.SRC, Component.LIB32]
        )
        assert base_jail_factory.get_snapshot_name(
            distribution.components) == f"{base_jail_factory.SNAPSHOT_NAME}_lib32_src"

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

        create_dummy_base_jail()
        try:
            assert base_jail_factory.base_jail_exists(TEST_DISTRIBUTION)
        finally:
            destroy_dummy_base_jail()

    def test_exists_base_jail_multiple_components(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        distribution = Distribution(version=TEST_DISTRIBUTION.version,
                                    architecture=TEST_DISTRIBUTION.architecture,
                                    components=[Component.SRC])
        create_dummy_base_jail()
        try:
            assert not base_jail_factory.base_jail_exists(distribution)
        finally:
            destroy_dummy_base_jail()

        create_dummy_base_jail(distribution=distribution)
        try:
            jail_exists = base_jail_factory.base_jail_exists(distribution)
            assert jail_exists
        finally:
            destroy_dummy_base_jail(distribution=distribution)

    def test_destroy_base_jail(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        create_dummy_base_jail()

        base_jail_factory.destroy_base_jail(TEST_DISTRIBUTION)
        assert not base_jail_factory.base_jail_exists(distribution=TEST_DISTRIBUTION)
        assert not len(base_jail_factory.list_base_jails())

    def test_destroy_base_jail_with_accumulative_components(self):
        distribution = Distribution(version=TEST_DISTRIBUTION.version,
                                    architecture=TEST_DISTRIBUTION.architecture,
                                    components=[Component.SRC, Component.LIB32])
        lib32_distribution = Distribution(version=TEST_DISTRIBUTION.version,
                                          architecture=TEST_DISTRIBUTION.architecture,
                                          components=[Component.LIB32])
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        create_dummy_base_jail()
        create_dummy_base_jail(distribution=distribution)
        create_dummy_base_jail(distribution=lib32_distribution)

        base_jail_factory.destroy_base_jail(distribution)
        assert base_jail_factory.base_jail_exists(distribution=TEST_DISTRIBUTION)
        assert base_jail_factory.base_jail_exists(distribution=lib32_distribution)
        assert not base_jail_factory.base_jail_exists(distribution=distribution)

        base_jail_factory.destroy_base_jail(lib32_distribution)
        assert base_jail_factory.base_jail_exists(distribution=TEST_DISTRIBUTION)
        assert not base_jail_factory.base_jail_exists(distribution=lib32_distribution)
        assert not base_jail_factory.base_jail_exists(distribution=distribution)

        base_jail_factory.destroy_base_jail(TEST_DISTRIBUTION)
        assert not base_jail_factory.base_jail_exists(distribution=TEST_DISTRIBUTION)
        assert not base_jail_factory.base_jail_exists(distribution=lib32_distribution)
        assert not base_jail_factory.base_jail_exists(distribution=distribution)

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

    def test_get_origin_from_jail(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        create_dummy_base_jail()
        try:
            create_dummy_jail(jail_name=TEST_JAIL_NAME)
            gathered_distribution = base_jail_factory.get_origin_from_jail('test')
            assert gathered_distribution == TEST_DISTRIBUTION
        finally:
            destroy_dummy_jail(jail_name=TEST_JAIL_NAME)
            destroy_dummy_base_jail()

    def test_get_origin_from_jail_with_several_components(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        distribution = Distribution(
            version=TEST_DISTRIBUTION.version,
            architecture=TEST_DISTRIBUTION.architecture,
            components=[Component.SRC]
        )

        create_dummy_base_jail(distribution=distribution)
        try:
            create_dummy_jail(TEST_JAIL_NAME, distribution=distribution)
            assert base_jail_factory.get_origin_from_jail(TEST_JAIL_NAME) == distribution
        finally:
            destroy_dummy_jail(TEST_JAIL_NAME)
            destroy_dummy_base_jail(distribution)

    def test_list_base_jails(self):
        base_jail_factory = get_mocking_base_jail_factory(TMP_PATH)
        distribution = Distribution(
            version=TEST_DISTRIBUTION.version,
            architecture=TEST_DISTRIBUTION.architecture,
            components=[Component.SRC]
        )

        create_dummy_base_jail()
        create_dummy_base_jail(distribution=distribution)
        try:
            list_of_base_jails = base_jail_factory.list_base_jails()

            assert len(list_of_base_jails) == 2
            assert TEST_DISTRIBUTION in list_of_base_jails
            assert distribution in list_of_base_jails

        finally:
            destroy_dummy_base_jail()

        assert not len(base_jail_factory.list_base_jails())
