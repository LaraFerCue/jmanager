from jmanager.models.distribution import Distribution, Component
from src.test.globals import get_mocking_base_jail_factory, TMP_PATH, TEST_DISTRIBUTION, create_dummy_base_jail, \
    destroy_dummy_base_jail


class TestBaseJailFactoryCheckers:
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
