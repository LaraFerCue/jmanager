from typing import List, Dict

import pytest

from src.configuration import parse_jmanagerfile
from src.test.globals import RESOURCES_PATH

SAMPLE_JMANAGER_FILE = RESOURCES_PATH.joinpath('test_jmanagerfile.yaml')
JAIL_CONFIGURATION_EXAMPLE: List[Dict] = [
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

JAIL_PARAMETERS = {
    "exec.start": "true",
    "exec.stop": "false"
}


class TestJManagerFile:
    def test_parsing_correct_configuration(self):
        jmanager_file = parse_jmanagerfile(JAIL_CONFIGURATION_EXAMPLE)

        assert jmanager_file[0].jail.name == JAIL_CONFIGURATION_EXAMPLE[0]['name']
        assert str(jmanager_file[0].distribution.version) == JAIL_CONFIGURATION_EXAMPLE[0]['version']
        assert jmanager_file[0].distribution.architecture.value == JAIL_CONFIGURATION_EXAMPLE[0]['architecture']
        for component in jmanager_file[0].distribution.components:
            assert component.value in ['base', *JAIL_CONFIGURATION_EXAMPLE[0]['components']]

    def test_parsing_with_parameters(self):
        configuration = JAIL_CONFIGURATION_EXAMPLE.copy()
        configuration[0]['jail_parameters'] = JAIL_PARAMETERS.copy()

        for jail in parse_jmanagerfile(jail_dictionary_list=configuration):
            for parameter, value in jail.jail.parameters.items():
                assert parameter.value in JAIL_PARAMETERS.keys()
                assert value == JAIL_PARAMETERS[parameter.value]

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
