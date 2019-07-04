from pathlib import PosixPath
from typing import List, Dict, Union

import pytest

from src.configuration import parse_jmanagerfile

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

        assert jail_list[0].jail.name == JAIL_CONFIGURATION_EXAMPLE[0]['name']
        assert str(jail_list[0].distribution.version) == JAIL_CONFIGURATION_EXAMPLE[0]['version']
        assert jail_list[0].distribution.architecture.value == JAIL_CONFIGURATION_EXAMPLE[0]['architecture']
        for component in jail_list[0].distribution.components:
            assert component.value in JAIL_CONFIGURATION_EXAMPLE[0]['components']

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
