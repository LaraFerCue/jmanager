from pathlib import PosixPath
from tempfile import TemporaryDirectory
from typing import List

from models.distribution import Distribution
from models.jail import Jail, JailError
from src.factories.jail_factory import JailFactory
from src.utils.fetch import HTTPFetcher
from src.utils.provision import Provision


def get_progress_text(msg: str, iteration: int, total: int) -> str:
    percent = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(50 * iteration // total)
    bar = '=' * filled_length + ' ' * (50 - filled_length)

    return "%s |%s| %s%%" % (msg, bar, percent)


def print_progress_bar_extract(msg: str, iteration: int, total: int):
    progress_text = get_progress_text(msg, iteration, total)

    print('\r%s ' % progress_text, end='\r')
    if iteration == total:
        print()


class JailManager:
    def __init__(self, http_fetcher: HTTPFetcher, jail_factory: JailFactory):
        self._http_fetcher = http_fetcher
        self._jail_factory = jail_factory
        self._iteration = 0
        self._speed = 0
        self._provision = Provision()

    def print_progress_bar_fetch(self, msg, iteration, total, speed):
        progress_text = get_progress_text(msg, iteration, total)

        if (self._iteration % 250) == 0:
            self._speed = speed
        self._iteration += 1

        print('\r%s %2.2f Mbps  ' % (progress_text, self._speed / 1e6), end='\r')
        if iteration == total:
            self._iteration = 0
            print()

    def create_jail(self, jail_data: Jail, distribution: Distribution):
        if not self._jail_factory.base_jail_factory.base_jail_exists(distribution=distribution):
            with TemporaryDirectory(prefix="jmanager_", suffix="_tarballs") as temp_dir:
                path_to_temp_dir = PosixPath(temp_dir)
                self._http_fetcher.fetch_tarballs_into(
                    version=distribution.version,
                    architecture=distribution.architecture,
                    components=distribution.components,
                    temp_dir=path_to_temp_dir,
                    callback=self.print_progress_bar_fetch)
                self._jail_factory.base_jail_factory.create_base_jail(distribution=distribution,
                                                                      path_to_tarballs=path_to_temp_dir,
                                                                      callback=print_progress_bar_extract)

        self._jail_factory.create_jail(jail_data=jail_data, distribution=distribution)

    def destroy_jail(self, jail_name: str):
        if self._jail_factory.jail_exists(jail_name):
            self._jail_factory.destroy_jail(jail_name)
        else:
            raise JailError(f"No jail named '{jail_name}'")

    def list_jails(self) -> List[Jail]:
        return self._jail_factory.list_jails()

    def list_base_jails(self) -> List[Distribution]:
        return self._jail_factory.base_jail_factory.list_base_jails()

    def start(self, jail_name: str):
        self._jail_factory.start_jail(jail_name)

    def stop(self, jail_name: str):
        self._jail_factory.stop_jail(jail_name)
