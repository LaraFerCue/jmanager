#!/usr/bin/env python3

import argparse
from pathlib import PosixPath

from src.configuration import read_configuration_file, parse_jmanagerfile

parser = argparse.ArgumentParser(description="Jail Manager")
parser.add_argument("--jmanager-config",
                    type=str,
                    help="path to the configuration file for the program",
                    default='/usr/local/etc/jmanager.conf')
parser.add_argument("--jmanagerfile",
                    type=str,
                    help="path to the configuration file for the jail to create",
                    default="./Jmanagerfile")

args = parser.parse_args()

config_file_path = PosixPath(args.jmanager_config)
configuration = read_configuration_file(config_file_path)
print(configuration)

jmanagerfile_path = PosixPath(args.jmanagerfile)
jail = parse_jmanagerfile(read_configuration_file(jmanagerfile_path))
