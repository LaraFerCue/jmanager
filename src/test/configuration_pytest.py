from pathlib import PosixPath

import pytest

from models.config import Config
from src.configuration import read_configuration_file
from src.test.jmanagerfile_pytest import SAMPLE_JMANAGER_FILE, JAIL_CONFIGURATION_EXAMPLE

SAMPLE_CONFIGURATION = {
    'zfs_pool': 'zpool',
    'jail_base_path': '/usr/jails',
    'user': 'jmanager'
}


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


class TestConfiguration:
    def test_configuration_without_errors(self):
        configuration = Config.from_dictionary(SAMPLE_CONFIGURATION)
        assert configuration.zfs_pool == SAMPLE_CONFIGURATION['zfs_pool']
        assert configuration.jail_base_path.as_posix() == SAMPLE_CONFIGURATION['jail_base_path']
        assert configuration.user == SAMPLE_CONFIGURATION['user']

    def test_configuration_with_wrong_zfs_pool_type(self):
        wrong_config = SAMPLE_CONFIGURATION.copy()
        wrong_config['zfs_pool'] = ['zpool']
        with pytest.raises(ValueError, match=r"zfs_pool must be of type 'str' found 'list'"):
            Config.from_dictionary(wrong_config)

    def test_configuration_with_wrong_jail_base_path_type(self):
        wrong_config = SAMPLE_CONFIGURATION.copy()
        wrong_config['jail_base_path'] = ['jail_base_path']
        with pytest.raises(ValueError, match=r"jail_base_path must be of type 'str' found 'list'"):
            Config.from_dictionary(wrong_config)

    def test_configuration_with_wrong_user_type(self):
        wrong_config = SAMPLE_CONFIGURATION.copy()
        wrong_config['user'] = ['user']
        with pytest.raises(ValueError, match=r"user must be of type 'str' found 'list'"):
            Config.from_dictionary(wrong_config)
