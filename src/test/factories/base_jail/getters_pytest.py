from models.distribution import Distribution, Component
from src.test.globals import get_mocking_base_jail_factory, TMP_PATH, TEST_DISTRIBUTION, create_dummy_base_jail, \
    destroy_dummy_base_jail


class TestBaseJailFactoryGetters:
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
