import os
import subprocess
from distutils.file_util import copy_file
from pathlib import PosixPath
from tempfile import TemporaryDirectory
from typing import List

from jmanager.utils.console_utils import print_progress_bar_extract, print_progress_bar_fetch
from jmanager.models.distribution import Distribution
from jmanager.models.jail import Jail, JailError
from src.factories.jail_factory import JailFactory
from src.utils.ansible import Ansible
from src.utils.fetch import HTTPFetcher
from src.utils.jail_configuration import create_private_key, configure_services, \
    configure_ssh_service_configuration_file, read_port_from_config_file, write_public_key


class JailManager:
    def __init__(self, http_fetcher: HTTPFetcher, jail_factory: JailFactory):
        self._http_fetcher = http_fetcher
        self._jail_factory = jail_factory
        self._ansible = Ansible()

        if not self._jail_factory.jail_config_folder.is_dir():
            os.makedirs(self._jail_factory.jail_config_folder.as_posix())
        if not self._jail_factory.jail_config_folder.joinpath(self._ansible.ANSIBLE_CONFIG_FILE).is_file():
            self._ansible.write_ansible_configuration(self._jail_factory.jail_config_folder)

        self._private_key_path = self._jail_factory.jail_config_folder.joinpath('priv.key')
        if not self._private_key_path.is_file():
            create_private_key(priv_key_file_path=self._private_key_path)

    def create_jail(self, jail_data: Jail, distribution: Distribution):
        if not self._jail_factory.base_jail_factory.base_jail_exists(distribution=distribution):
            with TemporaryDirectory(prefix="jmanager_", suffix="_tarballs") as temp_dir:
                print("Fetching tarballs ...")
                path_to_temp_dir = PosixPath(temp_dir)
                self._http_fetcher.fetch_tarballs_into(
                    version=distribution.version,
                    architecture=distribution.architecture,
                    components=distribution.components,
                    temp_dir=path_to_temp_dir,
                    callback=print_progress_bar_fetch)
                print("Creating the base jail ...")
                self._jail_factory.base_jail_factory.create_base_jail(distribution=distribution,
                                                                      path_to_tarballs=path_to_temp_dir,
                                                                      callback=print_progress_bar_extract)

        self._jail_factory.create_jail(jail_data=jail_data, distribution=distribution)
        list_of_jails = self._jail_factory.list_jails()
        self._ansible.write_inventory(list_of_jails=list_of_jails,
                                      config_folder=self._jail_factory.jail_config_folder)

    def destroy_jail(self, jail_name: str):
        if self._jail_factory.jail_exists(jail_name):
            self._jail_factory.destroy_jail(jail_name)
        else:
            raise JailError(f"No jail named '{jail_name}'")

    def list_jails(self) -> List[Jail]:
        return self._jail_factory.list_jails()

    def list_base_jails(self) -> List[Distribution]:
        return self._jail_factory.base_jail_factory.list_base_jails()

    def get_jail_mountpoint(self, jail_name: str) -> PosixPath:
        return self._jail_factory.base_jail_factory.get_jail_mountpoint(jail_data_set_name=jail_name)

    def start(self, jail_name: str):
        path_to_jail = self.get_jail_mountpoint(jail_name=jail_name)
        if not path_to_jail.joinpath('etc', 'resolv.conf').is_file():
            copy_file('/etc/resolv.conf', path_to_jail.joinpath('etc').as_posix())

        jail_config_file = self._jail_factory.get_config_file_path(jail_name)
        cmd = f"{self._jail_factory.JAIL_CMD} -f {jail_config_file} -c {jail_name}"
        return subprocess.run(cmd, shell=True, check=True,
                              universal_newlines=True).stdout

    def stop(self, jail_name: str):
        jail_config_file = self._jail_factory.get_config_file_path(jail_name)
        cmd = f"{self._jail_factory.JAIL_CMD} -f {jail_config_file} -r {jail_name}"
        return subprocess.run(cmd, shell=True, check=True,
                              universal_newlines=True).stdout

    def get_jail_port(self, jail_name: str) -> int:
        port = -1
        jail_path = self.get_jail_mountpoint(jail_name=jail_name)
        if jail_path.joinpath('etc', 'ssh', 'sshd_config').is_file():
            port = read_port_from_config_file(
                config_file_path=jail_path.joinpath('etc', 'ssh', 'sshd_config')
            )

        if port < 0:
            port = 2200 + len(self.list_jails())
        return port

    def configure_jail(self, jail_name: str):
        jail_path = self.get_jail_mountpoint(jail_name=jail_name)
        configure_ssh_service_configuration_file(
            path_to_config_file=jail_path.joinpath('etc', 'ssh', 'sshd_config'),
            jail_port=self.get_jail_port(jail_name=jail_name)
        )
        configure_services(service_configure_file_path=jail_path.joinpath('etc', 'rc.conf'))
        ssh_config_folder = jail_path.joinpath('root', '.ssh')
        if not ssh_config_folder.is_dir():
            os.makedirs(ssh_config_folder.as_posix())

        write_public_key(priv_key_path=self._private_key_path,
                         pub_key_path=ssh_config_folder.joinpath('authorized_keys'))

    def provision_jail(self, jail_name: str, provision_file: PosixPath = None):
        self._ansible.run_provision_cmd(cmd='pkg install -y python36', jail_name=jail_name,
                                        config_folder=self._jail_factory.jail_config_folder)
        if provision_file is not None:
            self._ansible.run_provision(path_to_playbook_file=provision_file,
                                        config_folder=self._jail_factory.jail_config_folder)
