from pathlib import PosixPath
from typing import List, Dict, Union, Any

from yaml import load, Loader

from jmanager.models.distribution import Architecture, Component, Version
from jmanager.models.jail_parameter import JailParameter
from jmanager.models.jmanagerfile import JManagerFile

CONFIGURATION_SCHEMA: Dict[str, type] = {
    'name': str,
    'version': str,
    'architecture': str,
    'components': list,
    'jail_parameters': dict,
    'provision': dict
}


def read_configuration_file(path_to_file: PosixPath) -> Union[List[Dict], Dict]:
    if not path_to_file.is_file():
        raise FileNotFoundError("error: The configuration file has not been found")

    with open(path_to_file.as_posix(), "r") as config_file:
        data = load(config_file.read(), Loader)
    return data


def parse_jmanagerfile(jail_dictionary_list: List[Dict[str, Any]]) -> List[JManagerFile]:
    jail_list: List[JManagerFile] = []

    for jail_dictionary in jail_dictionary_list:
        sanitize_input(jail_dictionary)

        components = []
        for component in jail_dictionary['components']:
            components.append(Component(component))

        jail_parameters: Dict[JailParameter, str] = {}
        if 'jail_parameters' in jail_dictionary:
            for parameter, value in jail_dictionary['jail_parameters'].items():
                jail_parameters[JailParameter(parameter)] = value
        provision = None
        if 'provision' in jail_dictionary:
            provision = jail_dictionary['provision']

        jail_list.append(JManagerFile(jail_name=jail_dictionary['name'],
                                      version=Version.from_string(jail_dictionary['version']),
                                      components=components,
                                      architecture=Architecture(jail_dictionary['architecture']),
                                      jail_parameters=jail_parameters,
                                      provision=provision
                                      ))
    return jail_list


def sanitize_input(jail_dictionary: Dict[str, Union[List, str]]):
    for key in jail_dictionary.keys():
        if type(jail_dictionary[key]) != CONFIGURATION_SCHEMA[key]:
            raise ValueError(
                f"Property {key} must be of type '{CONFIGURATION_SCHEMA[key].__name__}' not " +
                f"'{type(jail_dictionary[key]).__name__}'")
