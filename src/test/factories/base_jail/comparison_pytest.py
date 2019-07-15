from src.factories.base_jail_factory import BaseJailFactory
from src.factories.data_set_factory import DataSetFactory
from src.test.globals import TMP_PATH, TEST_DATA_SET


class TestBaseJailFactoryComparison:
    def test_base_jail_factory_equality(self):
        dsf1 = DataSetFactory(zfs_root_data_set=TEST_DATA_SET)
        dsf2 = DataSetFactory(zfs_root_data_set=TEST_DATA_SET)

        bf1 = BaseJailFactory(jail_root_path=TMP_PATH, data_set_factory=dsf1)
        bf2 = BaseJailFactory(jail_root_path=TMP_PATH, data_set_factory=dsf2)

        assert bf1 == bf2

    def test_base_jail_factory_inequality(self):
        dsf1 = DataSetFactory(zfs_root_data_set=TEST_DATA_SET)
        dsf2 = DataSetFactory(zfs_root_data_set=TEST_DATA_SET)

        bf1 = BaseJailFactory(jail_root_path=TMP_PATH.joinpath('other'), data_set_factory=dsf1)
        bf2 = BaseJailFactory(jail_root_path=TMP_PATH, data_set_factory=dsf2)

        assert bf1 != bf2
