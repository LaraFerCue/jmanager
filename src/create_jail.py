#!/usr/bin/env python3

import argparse
import sys
from pathlib import PosixPath
from typing import List, Dict

from yaml import Loader, load


def read_configuration_file(path_to_file: PosixPath) -> List[Dict[str, str]]:
    if not path_to_file.is_file():
        print("error: The configuration file has not been found", file=sys.stderr)

    with open(path_to_file.as_posix(), "r") as config_file:
        data = load(config_file.read(), Loader)
    return data


parser = argparse.ArgumentParser(description="Jail Manager")
parser.add_argument("--jail-config",
                    type=str,
                    help="path to the configuration file for the jail")

args = parser.parse_args()

config_file_path = PosixPath(args.jail_config)
data = read_configuration_file(config_file_path)
print(data)
