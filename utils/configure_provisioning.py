#!/usr/bin/python3

import yaml
import argparse

from pathlib import PosixPath

parser = argparse.ArgumentParser(description="Ansible hosts manager")
parser.add_argument("--hosts-file",
                    type=str,
                    help="Ansible's hosts file",
                    default="~/ansible-hosts")
parser.add_argument("--jail-name",
                    type=str,
                    help="Name of the jail to configure")
args = parser.parse_args()

hosts_file = PosixPath(args.hosts_file)

if hosts_file.is_file():
    with open(hosts_file.as_posix()) as hosts_fd:
        hosts_yaml = yaml.load(hosts_fd.read())
else:
    hosts_yaml = {
            "jails" : {
                'hosts': {
                    },
                'vars': {
                    'ansible_connection': 'jail',
                    'ansible_python_interpreter': '/usr/local/bin/python3.6'
                    }
                }
            }

hosts_yaml["jails"]["hosts"][args.jail_name] = { "hostname": args.jail_name}
print(hosts_yaml)

with open(hosts_file.as_posix(), 'w') as hosts_file:
    hosts_file.write(yaml.dump(hosts_yaml))
