import pytest

from models.distribution import Distribution, Component
from models.jail import Jail, JailError
from src.test.globals import get_mocking_jail_factory, create_dummy_base_jail, TEST_DISTRIBUTION, \
    destroy_dummy_base_jail, TMP_PATH, TEST_DATA_SET, destroy_dummy_jail, MockingZFS


class TestJailFactoryMultipleComponents:
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
        create_dummy_base_jail(distribution=distribution)

        try:
            jail_factory.create_jail(jail_data=jail_info, distribution=distribution)
            loaded_jail = Jail.read_jail_config_file(TMP_PATH.joinpath(jail_name, "jail.conf"))
            loaded_jail.origin = Distribution.read_config_file(
                TMP_PATH.joinpath(jail_name, 'distribution.conf')
            )
            assert loaded_jail.origin == distribution
            assert loaded_jail.name == jail_name
            assert MockingZFS().zfs_list(data_set=f"{TEST_DATA_SET}/{jail_name}")
            for option, value in jail_factory.get_jail_default_options(jail_info, TEST_DISTRIBUTION.version).items():
                assert loaded_jail.parameters[option] == value
        finally:
            destroy_dummy_jail(jail_name=jail_name)
            destroy_dummy_base_jail()
