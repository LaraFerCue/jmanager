from src.factories.base_jail_factory import BaseJailFactory
from src.factories.data_set_factory import DataSetFactory
from src.factories.jail_factory import JailFactory
from src.test.globals import TEST_DATA_SET, TMP_PATH


class TestJailFactoryComparison:
    def test_jail_factory_equality(self):
        dsf1 = DataSetFactory(zfs_root_data_set=TEST_DATA_SET)
        bjf1 = BaseJailFactory(data_set_factory=dsf1, jail_root_path=TMP_PATH)
        bjf2 = BaseJailFactory(data_set_factory=dsf1, jail_root_path=TMP_PATH)

        jf1 = JailFactory(base_jail_factory=bjf1, jail_config_folder=TMP_PATH)
        jf2 = JailFactory(base_jail_factory=bjf2, jail_config_folder=TMP_PATH)

        assert jf1 == jf2

    def test_jail_factory_inequality(self):
        dsf1 = DataSetFactory(zfs_root_data_set=TEST_DATA_SET)
        bjf = BaseJailFactory(data_set_factory=dsf1, jail_root_path=TMP_PATH)

        jf1 = JailFactory(base_jail_factory=bjf, jail_config_folder=TMP_PATH)
        jf2 = JailFactory(base_jail_factory=bjf, jail_config_folder=TMP_PATH.joinpath('other'))

        assert jf1 != jf2
