import os
import shutil

import pytest

from jmanager.models.jail import Jail, JailError
from test.globals import TEST_DATA_SET, TEST_DISTRIBUTION, create_dummy_base_jail, \
    get_mocking_jail_factory, TMP_PATH, destroy_dummy_base_jail, destroy_dummy_jail, MockingZFS


class TestJailFactory:
    def test_create_jail_without_options(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name)
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()

        try:
            jail_factory.create_jail(jail_data=jail_info, distribution=TEST_DISTRIBUTION)

            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(jail_name, "jail.conf"))
            assert loaded_jail.name == jail_name
            assert MockingZFS().zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            for option, value in jail_factory.get_jail_default_options(jail_info, TEST_DISTRIBUTION.version).items():
                assert loaded_jail.parameters[option] == value
        finally:
            destroy_dummy_jail(jail_name)
            destroy_dummy_base_jail()

    def test_create_jail_without_base_jail(self):
        jail_factory = get_mocking_jail_factory()
        with pytest.raises(JailError, match=r"The base jail for version 12.0-RELEASE/amd64/\['base'\] does not exist"):
            jail_factory.create_jail(jail_data=Jail('test'), distribution=TEST_DISTRIBUTION)

    def test_create_duplicated_jail(self):
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()
        MockingZFS().zfs_create(data_set=f"{TEST_DATA_SET}/test", options={})

        os.makedirs(TMP_PATH.joinpath('test').as_posix(), exist_ok=True)

        try:
            with pytest.raises(JailError, match=r"The jail 'test' already exists"):
                jail_factory.create_jail(jail_data=Jail('test'), distribution=TEST_DISTRIBUTION)

            shutil.rmtree(TMP_PATH.joinpath('test').as_posix(), ignore_errors=True)
            with pytest.raises(JailError,
                               match=r"The jail 'test' has some left overs, please remove them and try again."):
                jail_factory.create_jail(jail_data=Jail('test'), distribution=TEST_DISTRIBUTION)
        finally:
            destroy_dummy_jail('test')
            destroy_dummy_base_jail()

    def test_destroy_jail(self):
        jail_name = "test_no_options"
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()

        try:
            jail_factory.create_jail(jail_data=Jail(jail_name), distribution=TEST_DISTRIBUTION)
            jail_factory.destroy_jail(jail_name=jail_name)
            assert not TMP_PATH.joinpath(jail_name).is_dir()
            assert not len(MockingZFS().zfs_list(f"{TEST_DATA_SET}/{jail_name}"))
        finally:
            destroy_dummy_base_jail()

    def test_jail_exists(self):
        jail_factory = get_mocking_jail_factory()
        jail_name = "test_jail_exists"
        assert not jail_factory.jail_exists(jail_name)
        config_folder_path = TMP_PATH.joinpath(jail_name)
        os.makedirs(config_folder_path.as_posix(), exist_ok=True)

        open(config_folder_path.joinpath('jail.conf').as_posix(), 'w').close()
        open(config_folder_path.joinpath('distribution.conf').as_posix(), 'w').close()

        try:
            assert jail_factory.jail_exists(jail_name)
        finally:
            shutil.rmtree(config_folder_path.as_posix(), ignore_errors=True)

    def test_list_jails(self):
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()
        jail_factory.create_jail(jail_data=Jail('test'), distribution=TEST_DISTRIBUTION)

        try:
            jail_list = jail_factory.list_jails()
            assert len(jail_list) == 1
            assert jail_list[0].name == 'test'
            assert jail_list[0].origin == TEST_DISTRIBUTION
        finally:
            jail_factory.destroy_jail('test')
            destroy_dummy_base_jail()
