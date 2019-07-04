from pathlib import PosixPath
from typing import List, Dict, Union

from yaml import load, Loader

from models.distribution import Distribution, Architecture, Component, Version

CONFIGURATION_SCHEMA: Dict[str, type] = {
    'name': str,
    'version': str,
    'architecture': str,
    'components': list
}


def read_configuration_file(path_to_file: PosixPath) -> List[Dict[str, str]]:
    if not path_to_file.is_file():
        raise FileNotFoundError("error: The configuration file has not been found")

    with open(path_to_file.as_posix(), "r") as config_file:
        data = load(config_file.read(), Loader)
    return data


def parse_jmanagerfile(jail_dictionary_list: List[Dict[str, Union[List, str]]]) -> List[Distribution]:
    jail_list: List[Distribution] = []

    for jail_dictionary in jail_dictionary_list:
        sanitize_input(jail_dictionary)

        components = []
        for component in jail_dictionary['components']:
            components.append(Component(component))

        jail_list.append(Distribution(name=jail_dictionary['name'],
                                      version=Version.from_string(jail_dictionary['version']),
                                      components=components,
                                      architecture=Architecture(jail_dictionary['architecture'])
                                      ))
    return jail_list


def sanitize_input(jail_dictionary: Dict[str, Union[List, str]]):
    for key in jail_dictionary.keys():
        if type(jail_dictionary[key]) != CONFIGURATION_SCHEMA[key]:
            raise ValueError(
                f"Property {key} must be of type '{CONFIGURATION_SCHEMA[key].__name__}' not " +
                f"'{type(jail_dictionary[key]).__name__}'")
