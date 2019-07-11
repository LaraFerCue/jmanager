import subprocess
from pathlib import PosixPath

import yaml


class Provision:
    ANSIBLE_CMD = 'ansible-playbook-3.6'

    @staticmethod
    def write_ansible_playbook(path_to_file: PosixPath, ansible_playbook):
        with open(path_to_file.as_posix(), 'w') as playbook:
            yaml.dump(ansible_playbook, stream=playbook)

    def run_provision(self, path_to_playbook_file: PosixPath, wrap_output: bool = True):
        cmd = [
            self.ANSIBLE_CMD,
            path_to_playbook_file.as_posix()
        ]

        subprocess_options = {
            'shell': True, 'check': True, 'universal_newlines': True
        }
        if wrap_output:
            subprocess_options['stdout'] = subprocess.PIPE
            subprocess_options['stderr'] = subprocess.STDOUT
        subprocess.run(" ".join(cmd), **subprocess_options)
