from pathlib import PosixPath
from typing import List, Dict, Union

import pytest

from src.configuration import read_configuration_file, parse_jmanagerfile

SAMPLE_JMANAGER_FILE = PosixPath('src/test/resources/test_jmanagerfile.yaml')
JAIL_CONFIGURATION_EXAMPLE: List[Dict[str, Union[List[str], str]]] = [
    {
        "name": "test",
        "version": "12.0-RELEASE",
        "architecture": "amd64",
        "components": [
            "src",
            "lib32"
        ]
    }
]


class TestJmanagerfile:
    def test_parsing_correct_configuration(self):
        jail_list = parse_jmanagerfile(JAIL_CONFIGURATION_EXAMPLE)

        assert jail_list[0].name == JAIL_CONFIGURATION_EXAMPLE[0]['name']
        assert str(jail_list[0].version) == JAIL_CONFIGURATION_EXAMPLE[0]['version']
        assert jail_list[0].architecture == JAIL_CONFIGURATION_EXAMPLE[0]['architecture']
        assert set(jail_list[0].components) == set(JAIL_CONFIGURATION_EXAMPLE[0]['components'])

    def test_parsing_wrong_type_name(self):
        configuration = [JAIL_CONFIGURATION_EXAMPLE[0].copy()]
        configuration[0]['name'] = ['name']

        with pytest.raises(ValueError, match=r"Property name must be of type 'str' not 'list'"):
            parse_jmanagerfile(configuration)

    def test_parsing_wrong_version_type(self):
        configuration = [JAIL_CONFIGURATION_EXAMPLE[0].copy()]
        configuration[0]['version'] = ['version']

        with pytest.raises(ValueError, match=r"Property version must be of type 'str' not 'list'"):
            parse_jmanagerfile(configuration)

    def test_parsing_wrong_architecture_type(self):
        configuration = [JAIL_CONFIGURATION_EXAMPLE[0].copy()]
        configuration[0]['architecture'] = ['architecture']

        with pytest.raises(ValueError, match=r"Property architecture must be of type 'str' not 'list'"):
            parse_jmanagerfile(configuration)

    def test_parsing_wrong_components_type(self):
        configuration = [JAIL_CONFIGURATION_EXAMPLE[0].copy()]
        configuration[0]['components'] = 'components'

        with pytest.raises(ValueError, match=r"Property components must be of type 'list' not 'str'"):
            parse_jmanagerfile(configuration)


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
