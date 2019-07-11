from models.jail import Jail, JailOption
from src.test.globals import get_mocking_jail_factory, create_dummy_base_jail, TEST_DISTRIBUTION, TMP_PATH, \
    TEST_DATA_SET, destroy_dummy_base_jail, destroy_dummy_jail


class TestJailFactoryOption:
    def test_create_jail_overriding_default_options(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name, options={JailOption.HOSTNAME: "no host name"})
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()

        try:
            jail_factory.create_jail(jail_data=jail_info, distribution=TEST_DISTRIBUTION)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(jail_name, "jail.conf"))
            assert loaded_jail.name == jail_name
            assert jail_factory.base_jail_factory.ZFS_FACTORY.zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            assert loaded_jail.options[JailOption.HOSTNAME] == "no host name"
        finally:
            destroy_dummy_jail(jail_name)
            destroy_dummy_base_jail()

    def test_create_jail_with_additional_options(self):
        jail_name = "test_no_options"
        jail_info = Jail(name=jail_name, options={JailOption.IP4: "new"})
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()

        try:
            jail_factory.create_jail(jail_data=jail_info, distribution=TEST_DISTRIBUTION)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(jail_name, "jail.conf"))
            assert loaded_jail.name == jail_name
            assert jail_factory.base_jail_factory.ZFS_FACTORY.zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            assert loaded_jail.options[JailOption.IP4] == "new"
        finally:
            destroy_dummy_jail(jail_name)
            destroy_dummy_base_jail()
