import filecmp
from pathlib import PosixPath
from tempfile import TemporaryDirectory

import pytest

from jmanager.models.jail import Jail
from jmanager.models.jail_parameter import JailParameter
from test.globals import RESOURCES_PATH, TEST_DISTRIBUTION

JAIL_CONFIGURATION_DICT = {
    'name': 'jail_test_name',
    'path': '/temp/jail_test_name',
    'host.hostname': "jail_test_name",
    'osrelease': "12.0-STABLE",
    'osreldate': "1200086",
    'exec.start': "sh /etc/rc",
    'exec.stop': "sh /etc/rc.shutdown"
}

JAIL_CONFIGURATION_FILE = RESOURCES_PATH.joinpath('test_jail_default_options.conf')


class TestJail:
    def test_remove_comments_from_file(self):
        with open(RESOURCES_PATH.joinpath('comments_file').as_posix()) as comment_file:
            assert Jail.remove_comments(comment_file.read()) == "\n\nthis is the result"

    def test_remove_comments_from_file_without_comments(self):
        with open(RESOURCES_PATH.joinpath('file_without_comments').as_posix(), 'r') as file_without_comments:
            original_file = file_without_comments.read()
            assert Jail.remove_comments(original_file) == original_file

    def test_parse_jail_config_file_without_options(self):
        jail = Jail.read_jail_config_file(JAIL_CONFIGURATION_FILE)

        for key in JAIL_CONFIGURATION_DICT.keys():
            if key == 'name':
                assert jail.name == JAIL_CONFIGURATION_DICT[key]
            else:
                assert jail.parameters[JailParameter(key)] == JAIL_CONFIGURATION_DICT[key]

    def test_write_configuration_file_with_default_options(self):
        jail_options = {}
        for key, value in JAIL_CONFIGURATION_DICT.items():
            if key == "name":
                continue
            jail_options[JailParameter(key)] = value
        jail = Jail(JAIL_CONFIGURATION_DICT['name'], jail_options)

        with TemporaryDirectory() as temp_dir:
            config_file_path = PosixPath(f"{temp_dir}/jail.conf")
            jail.write_config_file(config_file_path)

            assert filecmp.cmp(JAIL_CONFIGURATION_FILE, config_file_path, shallow=False)

    def test_modify_origin_property(self):
        jail = Jail('name')
        assert jail.origin is None
        jail.origin = TEST_DISTRIBUTION
        assert jail.origin == TEST_DISTRIBUTION

        with pytest.raises(TypeError, match=r"Wrong type 'int' for attribute origin"):
            jail.origin = 1
