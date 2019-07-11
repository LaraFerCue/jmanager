import filecmp
from pathlib import PosixPath
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory

import pytest

from src.utils.provision import Provision

TEST_RESOURCES_PLAYBOOK = PosixPath('src/test/resources/playbook')


class MockingProvision(Provision):
    ANSIBLE_CMD = "sh scripts/ansible.sh"


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
            wrap_output=False
        )

        with pytest.raises(CalledProcessError):
            MockingProvision().run_provision(
                path_to_playbook_file=TEST_RESOURCES_PLAYBOOK.joinpath('none'),
                wrap_output=True)
