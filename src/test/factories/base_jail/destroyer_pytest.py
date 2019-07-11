from models.distribution import Distribution, Component
from src.test.globals import get_mocking_base_jail_factory, TMP_PATH, create_dummy_base_jail, TEST_DISTRIBUTION


class TestBaseJailFactoryDestroyer:
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