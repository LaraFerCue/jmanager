from pathlib import PosixPath
from tempfile import TemporaryDirectory
from typing import List, Dict

import pytest
import yaml

from jmanager.models.jmanagerfile import JManagerFile
from src.configuration import parse_jmanagerfile
from src.test.globals import RESOURCES_PATH, TEST_DISTRIBUTION

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

    def test_parsing_with_provision(self):
        configuration = [JAIL_CONFIGURATION_EXAMPLE[0].copy()]
        configuration[0]['provision'] = {'type': 'inline', 'provision': {}}

        jmanager_file = parse_jmanagerfile(configuration)
        assert jmanager_file[0].provision_file_path is not None

    def test_jmanagerfile_with_provision_file(self):
        with TemporaryDirectory() as temp_dir:
            provision_file_path = PosixPath(temp_dir).joinpath('provision')
            provision = {'type': 'file', 'path': provision_file_path.as_posix()}
            open(provision_file_path.as_posix(), 'w').close()
            jmamagerfile = JManagerFile(jail_name='test', version=TEST_DISTRIBUTION.version,
                                        architecture=TEST_DISTRIBUTION.architecture,
                                        components=[],
                                        provision=provision)

            assert jmamagerfile.provision_file_path == provision_file_path

    def test_jmanagerfile_with_wrong_provision_type(self):
        provision = {'type': 'none'}
        with pytest.raises(ValueError, match=r"Wrong value 'none' for provision type"):
            JManagerFile(jail_name='test', version=TEST_DISTRIBUTION.version,
                         architecture=TEST_DISTRIBUTION.architecture,
                         components=[],
                         provision=provision)

    def test_jmanagerfile_with_missing_path_line(self):
        provision = {'type': 'file'}

        with pytest.raises(AttributeError, match=r"Path is a mandatory option for the provision type 'file'"):
            JManagerFile(jail_name='test', version=TEST_DISTRIBUTION.version,
                         architecture=TEST_DISTRIBUTION.architecture,
                         components=[],
                         provision=provision)

    def test_jmanagerfile_with_missing_provision_file(self):
        with TemporaryDirectory() as temp_dir:
            provision_file_path = PosixPath(temp_dir).joinpath('provision')
            provision = {'type': 'file', 'path': provision_file_path.as_posix()}

            with pytest.raises(FileNotFoundError, match=r'^Provision file'):
                JManagerFile(jail_name='test', version=TEST_DISTRIBUTION.version,
                             architecture=TEST_DISTRIBUTION.architecture,
                             components=[],
                             provision=provision)

    def test_jmanagerfile_with_inline_provision(self):
        provision = {
            'type': 'inline',
            'provision': [
                {
                    'name': 'name',
                    'value': 'value'
                }
            ]
        }
        jmamagerfile = JManagerFile(jail_name='test', version=TEST_DISTRIBUTION.version,
                                    architecture=TEST_DISTRIBUTION.architecture,
                                    components=[],
                                    provision=provision)
        with open(jmamagerfile.provision_file_path.as_posix(), 'r') as provision_file:
            read_provision_file = yaml.load(stream=provision_file, Loader=yaml.Loader)

            assert len(provision['provision']) == len(read_provision_file)
            for index in range(0, len(provision['provision'])):
                assert 'hosts' in read_provision_file[index]
                assert 'tasks' in read_provision_file[index]

                read_tasks = read_provision_file[index]['tasks']
                for key, value in provision['provision'][index].items():
                    assert key in read_tasks[index] and read_tasks[index][key] == value
