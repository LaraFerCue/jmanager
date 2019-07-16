from enum import Enum
from pathlib import PosixPath
from typing import Dict, List

from jmanager.models.distribution import Distribution


class JailParameter(Enum):
    PATH = 'path'
    HOSTNAME = 'host.hostname'
    OS_RELEASE = 'osrelease'
    OS_REL_DATE = 'osreldate'
    EXEC_START = 'exec.start'
    EXEC_STOP = 'exec.stop'
    IP4 = 'ip4'
    IP4_ADDR = 'ip4.addr'
    IP4_SADDR_SEL = 'ip4.saddrsel'
    IP6 = 'ip6'
    IP6_ADDR = 'ip6.addr'
    IP6_SADDR_SEL = 'ip6.saddrsel'
    MOUNT_DEVFS = 'mount.devfs'


HEADER = '# This file has been writen with JManager. Please, do not modify it\n' \
         '# If any change is needed use JManager to modify the options and/or\n' \
         '# name.\n\n'


class Jail:
    def __init__(self, name: str, parameters: Dict[JailParameter, str] = None, distribution: Distribution = None):
        self._name = name
        self._options = {}
        if parameters is not None:
            self._options.update(parameters)

        self._origin: Distribution = distribution

    @property
    def name(self) -> str:
        return self._name

    @property
    def parameters(self) -> Dict[JailParameter, str]:
        return self._options

    @property
    def origin(self) -> Distribution:
        return self._origin

    @origin.setter
    def origin(self, value: Distribution):
        if not isinstance(value, Distribution):
            raise TypeError(f"Wrong type '{type(value).__name__}' for attribute origin")
        self._origin = value

    def write_config_file(self, file_path: PosixPath):
        with open(file_path.as_posix(), 'w') as config_file:
            config_file.write(HEADER)
            config_file.write(f"{self.name} " + "{\n")
            for option, value in self.parameters.items():
                config_file.write(f"\t{option.value} = \"{value}\";\n")
            config_file.write("}\n")

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
    def parse_options(lines_of_file: List[str]) -> Dict[JailParameter, str]:
        """
        Parses the options on the configuration file
        :param lines_of_file:
        :return:
        """
        options: Dict[JailParameter, str] = {}

        for line in lines_of_file:
            position_of_assignation = line.find('=')
            if position_of_assignation > 0:
                option = line.split('=')[0].strip()
                value = line.split('=')[1].strip()
                semicolon_position = value.find(';')
                value = value[:semicolon_position].strip('"')

                options[JailParameter(option)] = value
        return options

    @staticmethod
    def read_jail_config_file(config_file: PosixPath) -> 'Jail':

        with open(config_file.as_posix(), 'r') as jail_config_file:
            lines = Jail.remove_comments(jail_config_file.read())
        jail_name: str = Jail.get_jail_name_from_lines(lines.split('\n'))
        options: Dict[JailParameter, str] = Jail.parse_options(lines.split('\n'))
        return Jail(name=jail_name, parameters=options)


class JailError(BaseException):
    pass
