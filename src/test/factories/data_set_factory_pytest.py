from src.factories.data_set_factory import DataSetFactory
from src.test.globals import TEST_DATA_SET


class TestDataSetFactory:
    def test_data_set_factory_equality(self):
        dsf1 = DataSetFactory(TEST_DATA_SET)
        dsf2 = DataSetFactory(TEST_DATA_SET)

        assert dsf1 == dsf2

    def test_data_set_factory_inequality(self):
        dsf1 = DataSetFactory(TEST_DATA_SET)
        dsf2 = DataSetFactory(f"{TEST_DATA_SET}/more")

        assert dsf1 != dsf2
