from pathlib import PosixPath
from typing import List, Dict, Union

from yaml import load, Loader

from models.jail import Jail
from models.version import Version


def read_configuration_file(path_to_file: PosixPath) -> List[Dict[str, str]]:
    if not path_to_file.is_file():
        raise FileNotFoundError("error: The configuration file has not been found")

    with open(path_to_file.as_posix(), "r") as config_file:
        data = load(config_file.read(), Loader)
    return data


def parse_configuration_file(jail_dictionary_list: List[Dict[str, Union[List, str]]]) -> List[Jail]:
    jail_list: List[Jail] = []

    for jail_dictionary in jail_dictionary_list:
        jail_list.append(Jail(name=jail_dictionary['name'],
                              version=Version.from_string(jail_dictionary['version']),
                              components=jail_dictionary['components'],
                              architecture=jail_dictionary['architecture']
                              ))
    return jail_list
