from pathlib import PosixPath

import pytest

from src.configuration import read_configuration_file
from src.test.jmanagerfile_pytest import SAMPLE_JMANAGER_FILE, JAIL_CONFIGURATION_EXAMPLE


class TestConfigurationFile:
    def test_read_correct_configuration_file(self):
        read_configuration = read_configuration_file(SAMPLE_JMANAGER_FILE)

        assert len(read_configuration) == len(JAIL_CONFIGURATION_EXAMPLE)
        for i in range(0, len(read_configuration)):
            for key, value in JAIL_CONFIGURATION_EXAMPLE[i].items():
                assert key in read_configuration[i].keys()
                assert value == read_configuration[i][key]

    def test_read_missing_configuration_file(self):
        with pytest.raises(FileNotFoundError):
            read_configuration_file(PosixPath('test/resources/missing_file'))
