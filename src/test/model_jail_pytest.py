from models.jail import Jail, JailOption
from src.test.globals import RESOURCES_PATH

JAIL_CONFIGURATION_DICT = {
    'name': 'jail_test_name',
    'path': '/temp/jail_test_name',
    'host.hostname': "jail_test_name",
    'osrelease': "12.0-STABLE",
    'osreldate': "1200086",
    'exec.start': "sh /etc/rc",
    'exec.stop': "sh /etc/rc.shutdown"
}

JAIL_CONFIGURATION_FILES = {
    'no_options': RESOURCES_PATH.joinpath('test_jail_default_options.conf')
}


class TestJail:
    def test_remove_comments_from_file(self):
        with open(RESOURCES_PATH.joinpath('comments_file').as_posix()) as comment_file:
            assert Jail.remove_comments(comment_file.read()) == "\n\nthis is the result"

    def test_remove_comments_from_file_without_comments(self):
        with open(JAIL_CONFIGURATION_FILES['no_options'].as_posix(), 'r') as file_without_comments:
            original_file = file_without_comments.read()
            assert Jail.remove_comments(original_file) == original_file

    def test_parse_jail_config_file_without_options(self):
        jail = Jail.read_jail_config_file(JAIL_CONFIGURATION_FILES['no_options'])

        for key in JAIL_CONFIGURATION_DICT.keys():
            if key == 'name':
                assert jail.name == JAIL_CONFIGURATION_DICT[key]
            else:
                assert jail.options[JailOption(key)] == JAIL_CONFIGURATION_DICT[key]
