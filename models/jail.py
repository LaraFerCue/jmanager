from enum import Enum
from pathlib import PosixPath
from typing import Dict, List


class JailOption(Enum):
    PATH = 'path'
    HOSTNAME = 'host.hostname'
    OS_RELEASE = 'osrelease'
    OS_REL_DATE = 'osreldate'
    EXEC_START = 'exec.start'
    EXEC_STOP = 'exec.stop'


class Jail:
    def __init__(self, name: str, options: Dict[JailOption, str] = None):
        self._name = name
        self._options = {}
        if options is not None:
            self._options.update(options)

    @property
    def name(self) -> str:
        return self._name

    @property
    def options(self) -> Dict[JailOption, str]:
        return self._options

    @staticmethod
    def get_jail_name_from_lines(lines_of_file: List[str]) -> str:
        for line in lines_of_file:
            position_opening_brace = line.find('{')
            if position_opening_brace > 0:
                return line[0:position_opening_brace].strip()

    @staticmethod
    def remove_comments(string: str) -> str:
        def _remove_comments(_string: str, start_comment: str, end_comment: str) -> str:
            while True:
                start_position = _string.find(start_comment)
                if start_position < 0:
                    break
                end_position = _string.find(end_comment, start_position) + len(end_comment)
                _string = _string[:start_position] + _string[end_position:]
            return _string

        string = _remove_comments(string, '/*', '*/')
        string = _remove_comments(string, '//', '\n')
        string = _remove_comments(string, '#', '\n')
        return string

    @staticmethod
    def parse_options(lines_of_file: List[str]) -> Dict[JailOption, str]:
        """
        Parses the options on the configuration file
        :param lines_of_file:
        :return:
        """
        options: Dict[JailOption, str] = {}

        for line in lines_of_file:
            position_of_assignation = line.find('=')
            if position_of_assignation > 0:
                option = line.split('=')[0].strip()
                value = line.split('=')[1].strip()
                semicolon_position = value.find(';')
                value = value[:semicolon_position].strip('"')

                options[JailOption(option)] = value
        return options

    @staticmethod
    def read_jail_config_file(config_file: PosixPath) -> 'Jail':

        with open(config_file.as_posix(), 'r') as jail_config_file:
            lines = Jail.remove_comments(jail_config_file.read())
        jail_name: str = Jail.get_jail_name_from_lines(lines.split('\n'))
        options: Dict[JailOption, str] = Jail.parse_options(lines.split('\n'))
        return Jail(name=jail_name, options=options)
