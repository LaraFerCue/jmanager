from pathlib import PosixPath
from tempfile import mkstemp
from typing import List, Dict

import pytest
import yaml

from src.configuration import read_configuration_file, parse_configuration_file

SAMPLE_CONFIGURATION_FILE = PosixPath('test/resources/test_config_file.yaml')
JAIL_CONFIGURATION_EXAMPLE: List[Dict[str, str]] = [
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


def write_configuration_file(configuration: List[Dict[str, str]],
                             tmp_directory: str) -> PosixPath:
    _, tempfile = mkstemp(dir=tmp_directory)

    with open(tempfile, "w") as yaml_file:
        yaml.dump(data=configuration, stream=yaml_file)
    return tempfile


class TestConfigurationFile:
    def test_read_correct_configuration_file(self):
        read_configuration = read_configuration_file(SAMPLE_CONFIGURATION_FILE)

        assert len(read_configuration) == len(JAIL_CONFIGURATION_EXAMPLE)
        for i in range(0, len(read_configuration)):
            for key, value in JAIL_CONFIGURATION_EXAMPLE[i].items():
                assert key in read_configuration[i].keys()
                assert value == read_configuration[i][key]

    def test_read_missing_configuration_file(self):
        with pytest.raises(FileNotFoundError):
            read_configuration_file(PosixPath('test/resources/missing_file'))

    def test_parsing_correct_configuration(self):
        jail_list = parse_configuration_file(JAIL_CONFIGURATION_EXAMPLE)

        assert jail_list[0].name == JAIL_CONFIGURATION_EXAMPLE[0]['name']
        assert str(jail_list[0].version) == JAIL_CONFIGURATION_EXAMPLE[0]['version']
        assert jail_list[0].architecture == JAIL_CONFIGURATION_EXAMPLE[0]['architecture']
        assert set(jail_list[0].components) == set(JAIL_CONFIGURATION_EXAMPLE[0]['components'])
