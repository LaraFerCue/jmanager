#!/usr/bin/env python3

import argparse
from pathlib import PosixPath

from src.configuration import read_jmanagerfile

parser = argparse.ArgumentParser(description="Jail Manager")
parser.add_argument("--jail-config",
                    type=str,
                    help="path to the configuration file for the jail")

args = parser.parse_args()

config_file_path = PosixPath(args.jail_config)
read_jmanagerfile(config_file_path)
