import pytest

from models.distribution import Distribution, Component
from models.jail import Jail, JailOption, JailError
from src.test.globals import TEST_DATA_SET, TEST_DISTRIBUTION, create_dummy_base_jail, \
    get_mocking_jail_factory, TMP_PATH, destroy_dummy_base_jail, DUMMY_BASE_JAIL_DATA_SET


class TestJailFactory:
    def test_create_jail_without_options(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name)
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()

        try:
            jail_factory.create_jail(jail_data=jail_info, distribution=TEST_DISTRIBUTION)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(f"{jail_name}.conf"))
            assert loaded_jail.name == jail_name
            assert jail_factory.base_jail_factory.ZFS_FACTORY.zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            for option, value in jail_factory.get_jail_default_options(jail_info, TEST_DISTRIBUTION.version).items():
                assert loaded_jail.options[option] == value
        finally:
            if jail_factory.jail_exists(jail_name):
                jail_factory.base_jail_factory.ZFS_FACTORY.zfs_destroy(data_set=f"{TEST_DATA_SET}/{jail_name}")
            destroy_dummy_base_jail()
            TMP_PATH.joinpath(f"{jail_name}.conf").unlink()

    def test_create_jail_for_distribution_with_several_components_and_no_base_jail(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name)
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()
        distribution = Distribution(version=TEST_DISTRIBUTION.version,
                                    architecture=TEST_DISTRIBUTION.architecture,
                                    components=[Component.SRC]
                                    )
        try:
            exception_message = r"The base jail for version 12.0-RELEASE/amd64/\['base', 'src'\] does not exist"
            with pytest.raises(JailError, match=exception_message):
                jail_factory.create_jail(jail_data=jail_info, distribution=distribution)
        finally:
            destroy_dummy_base_jail()

    def test_create_jail_for_distribution_with_several_components(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name)
        jail_factory = get_mocking_jail_factory()
        distribution = Distribution(version=TEST_DISTRIBUTION.version,
                                    architecture=TEST_DISTRIBUTION.architecture,
                                    components=[Component.SRC]
                                    )
        snapshot_name = jail_factory.base_jail_factory.get_snapshot_name(distribution=distribution)
        create_dummy_base_jail()
        jail_factory.base_jail_factory.ZFS_FACTORY.zfs_snapshot(
            data_set=DUMMY_BASE_JAIL_DATA_SET,
            snapshot_name=snapshot_name
        )

        try:
            jail_factory.create_jail(jail_data=jail_info, distribution=distribution)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(f"{jail_name}.conf"))
            assert loaded_jail.name == jail_name
            assert jail_factory.base_jail_factory.ZFS_FACTORY.zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            for option, value in jail_factory.get_jail_default_options(jail_info, TEST_DISTRIBUTION.version).items():
                assert loaded_jail.options[option] == value
        finally:
            if jail_factory.jail_exists(jail_name):
                jail_factory.base_jail_factory.ZFS_FACTORY.zfs_destroy(data_set=f"{TEST_DATA_SET}/{jail_name}")
            jail_factory.base_jail_factory.ZFS_FACTORY.zfs_destroy(
                data_set=f"{DUMMY_BASE_JAIL_DATA_SET}@{snapshot_name}"
            )
            destroy_dummy_base_jail()
            TMP_PATH.joinpath(f"{jail_name}.conf").unlink()

    def test_create_jail_overriding_default_options(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name, options={JailOption.HOSTNAME: "no host name"})
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()

        try:
            jail_factory.create_jail(jail_data=jail_info, distribution=TEST_DISTRIBUTION)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(f"{jail_name}.conf"))
            assert loaded_jail.name == jail_name
            assert jail_factory.base_jail_factory.ZFS_FACTORY.zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            assert loaded_jail.options[JailOption.HOSTNAME] == "no host name"
        finally:
            if jail_factory.jail_exists(jail_name):
                jail_factory.base_jail_factory.ZFS_FACTORY.zfs_destroy(data_set=f"{TEST_DATA_SET}/{jail_name}")
            destroy_dummy_base_jail()
            TMP_PATH.joinpath(f"{jail_name}.conf").unlink()

    def test_create_jail_with_additional_options(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name, options={JailOption.IP4: "new"})
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()

        try:
            jail_factory.create_jail(jail_data=jail_info, distribution=TEST_DISTRIBUTION)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(f"{jail_name}.conf"))
            assert loaded_jail.name == jail_name
            assert jail_factory.base_jail_factory.ZFS_FACTORY.zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            assert loaded_jail.options[JailOption.IP4] == "new"
        finally:
            jail_factory.base_jail_factory.ZFS_FACTORY.zfs_destroy(data_set=f"{TEST_DATA_SET}/{jail_name}",
                                                                   arguments=['-R'])
            destroy_dummy_base_jail()
            TMP_PATH.joinpath(f"{jail_name}.conf").unlink()

    def test_create_jail_without_base_jail(self):
        jail_factory = get_mocking_jail_factory()
        with pytest.raises(JailError, match=r"The base jail for version 12.0-RELEASE/amd64/\['base'\] does not exist"):
            jail_factory.create_jail(jail_data=Jail('test'), distribution=TEST_DISTRIBUTION)

    def test_create_duplicated_jail(self):
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()
        jail_factory.base_jail_factory.ZFS_FACTORY.zfs_create(data_set=f"{TEST_DATA_SET}/test", options={})

        with open(TMP_PATH.joinpath('test.conf').as_posix(), "w") as fd:
            fd.write("test\n")

        try:
            with pytest.raises(JailError, match=r"The jail 'test' already exists"):
                jail_factory.create_jail(jail_data=Jail('test'), distribution=TEST_DISTRIBUTION)

            TMP_PATH.joinpath('test.conf').unlink()
            with pytest.raises(JailError,
                               match=r"The jail 'test' has some left overs, please remove them and try again."):
                jail_factory.create_jail(jail_data=Jail('test'), distribution=TEST_DISTRIBUTION)
        finally:
            jail_factory.base_jail_factory.ZFS_FACTORY.zfs_destroy(data_set=f"{TEST_DATA_SET}/test")
            destroy_dummy_base_jail()

    def test_jail_exists(self):
        jail_factory = get_mocking_jail_factory()
        jail_name = "test_jail_exists"
        assert not jail_factory.jail_exists(jail_name)
        open(TMP_PATH.joinpath(f'{jail_name}.conf').as_posix(), 'w').close()

        try:
            assert jail_factory.jail_exists(jail_name)
        finally:
            TMP_PATH.joinpath(f'{jail_name}.conf').unlink()

    def test_destroy_jail(self):
        jail_name = "test_no_options"
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()

        try:
            jail_factory.create_jail(jail_data=Jail(jail_name), distribution=TEST_DISTRIBUTION)
            jail_factory.destroy_jail(jail_name=jail_name)
            assert not TMP_PATH.joinpath(f"{jail_name}.conf").is_file()
            assert not len(jail_factory.base_jail_factory.ZFS_FACTORY.zfs_list(f"{TEST_DATA_SET}/{jail_name}"))
        finally:
            destroy_dummy_base_jail()

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
