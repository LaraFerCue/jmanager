import subprocess
from pathlib import PosixPath
from typing import List, Dict

import yaml

from models.jail import Jail


class Provision:
    ANSIBLE_PLAYBOOK_CMD = 'ansible-playbook-3.6'
    ANSIBLE_CMD = 'ansible-3.6'
    ANSIBLE_INVENTORY_NAME = 'ansible_inventory'
    ANSIBLE_CONFIG_FILE = 'ansible.cfg'

    @staticmethod
    def write_ansible_playbook(path_to_file: PosixPath, ansible_playbook):
        with open(path_to_file.as_posix(), 'w') as playbook:
            yaml.dump(ansible_playbook, stream=playbook)

    def run_provision_cmd(self, cmd: str, jail_name: str, config_folder: PosixPath):
        cmd.replace("'", "\\'")
        cmd = [
            f'env ANSIBLE_CONFIG={config_folder.as_posix()}/{self.ANSIBLE_CONFIG_FILE}',
            self.ANSIBLE_CMD,
            f"--inventory={config_folder.joinpath(self.ANSIBLE_INVENTORY_NAME).as_posix()}",
            f"--module-name=raw",
            f"--args='{cmd}'",
            jail_name
        ]
        subprocess.run(" ".join(cmd), shell=True, check=True, universal_newlines=True)

    def run_provision(self, path_to_playbook_file: PosixPath):
        cmd = [
            self.ANSIBLE_PLAYBOOK_CMD,
            path_to_playbook_file.as_posix()
        ]

        subprocess.run(" ".join(cmd), shell=True, check=True, universal_newlines=True)

    def write_inventory(self, list_of_jails: List[Jail], config_folder: PosixPath):
        inventory: Dict = {
            'all': {
                'hosts': {},
                'vars': {
                    'ansible_python_interpreter': '/usr/local/bin/python3.6'
                }
            }
        }
        port = 2201
        for jail in list_of_jails:
            inventory['all']['hosts'][jail.name] = {
                'ansible_host': 'localhost',
                'ansible_user': 'root',
                'ansible_port': port
            }
            port += 1
        with open(config_folder.joinpath(self.ANSIBLE_INVENTORY_NAME).as_posix(), 'w') as inventory_file:
            yaml.dump(inventory, stream=inventory_file)

    def write_ansible_configuration(self, config_folder: PosixPath):
        with open(config_folder.joinpath(self.ANSIBLE_CONFIG_FILE).as_posix(), 'w') as ansible_config_file:
            ansible_config_file.write("[defaults]\n")
            ansible_config_file.write(f"inventory = {config_folder.joinpath(self.ANSIBLE_INVENTORY_NAME)}\n\n")

            ansible_config_file.write('[ssh_connection]\n')
            priv_key_path = config_folder.joinpath("priv.key")
            ansible_config_file.write(
                f'ssh_args = -C -o ControlMaster=auto -o ControlPersist=60s -i {priv_key_path.as_posix()}\n')
