import filecmp
from pathlib import PosixPath
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory

import pytest

from models.jail import Jail
from src.test.globals import TMP_PATH
from src.utils.provision import Provision

TEST_RESOURCES_PLAYBOOK = PosixPath('src/test/resources/playbook')


class MockingProvision(Provision):
    ANSIBLE_PLAYBOOK_CMD = "sh scripts/ansible-playbook.sh"
    ANSIBLE_CMD = 'sh scripts/ansible.sh'


def configure_ansible_template(temp_folder_path: str, filename: str):
    with open('src/test/resources/ansible.cfg', 'r') as template:
        with open(f"{temp_folder_path}/{filename}", 'w') as temp_file:
            temp_file.write(template.read().replace('%temp%', temp_folder_path))


class TestProvision:
    def test_write_playbook(self):
        configuration = [{
            'block1': {'name': 'hello'}
        }]
        with TemporaryDirectory() as temp_dir:
            playbook_path = PosixPath(temp_dir).joinpath('test')
            MockingProvision().write_ansible_playbook(playbook_path,
                                                      configuration)
            assert filecmp.cmp(playbook_path.as_posix(), TEST_RESOURCES_PLAYBOOK.as_posix())

    def test_run_playbook(self):
        MockingProvision().run_provision(
            path_to_playbook_file=TEST_RESOURCES_PLAYBOOK,
        )

        with pytest.raises(CalledProcessError):
            MockingProvision().run_provision(
                path_to_playbook_file=TEST_RESOURCES_PLAYBOOK.joinpath('none'))

    def test_create_ansible_configuration(self):
        with TemporaryDirectory() as temp_dir:
            MockingProvision().write_ansible_configuration(PosixPath(temp_dir))
            configure_ansible_template(temp_dir, 'config')
            assert filecmp.cmp(f"{temp_dir}/ansible.cfg", f"{temp_dir}/config", shallow=False)

    def test_write_inventory_file(self):
        MockingProvision().write_inventory([Jail('test1'), Jail('test2')], TMP_PATH)
        assert filecmp.cmp(TMP_PATH.joinpath('ansible_inventory').as_posix(), 'src/test/resources/ansible_inventory')

    def test_run_provision_cmd(self):
        cmd = 'echo true'

        MockingProvision().run_provision_cmd(cmd, 'test', config_folder=TMP_PATH)
