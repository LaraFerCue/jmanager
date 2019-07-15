import os
import subprocess
from distutils.file_util import copy_file
from pathlib import PosixPath
from tempfile import TemporaryDirectory
from typing import List, Dict

from jmanager.utils.console_utils import print_progress_bar_extract, print_progress_bar_fetch
from models.distribution import Distribution
from models.jail import Jail, JailError
from src.factories.jail_factory import JailFactory
from src.utils.fetch import HTTPFetcher
from src.utils.provision import Provision


class JailManager:
    def __init__(self, http_fetcher: HTTPFetcher, jail_factory: JailFactory):
        self._http_fetcher = http_fetcher
        self._jail_factory = jail_factory
        self._provision = Provision()

        if not self._jail_factory.jail_config_folder.is_dir():
            os.makedirs(self._jail_factory.jail_config_folder.as_posix())
        if not self._jail_factory.jail_config_folder.joinpath(self._provision.ANSIBLE_CONFIG_FILE).is_file():
            self._provision.write_ansible_configuration(self._jail_factory.jail_config_folder)

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
        self._provision.write_inventory(list_of_jails=list_of_jails,
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

    def provision_jail(self, jail_name: str, provision_dict: Dict):
        self._provision.run_provision_cmd(cmd='pkg install -y python3.6', jail_name=jail_name,
                                          config_folder=self._jail_factory.jail_config_folder)
