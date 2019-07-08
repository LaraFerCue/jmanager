from pathlib import PosixPath
from tempfile import TemporaryDirectory
from typing import List

from models.distribution import Distribution
from models.jail import Jail
from src.factories.jail_factory import JailFactory, JailError
from src.utils.fetch import HTTPFetcher


class JailManager:
    def __init__(self, http_fetcher: HTTPFetcher, jail_factory: JailFactory):
        self._http_fetcher = http_fetcher
        self._jail_factory = jail_factory

    @staticmethod
    def print_progress_bar(msg, iteration, total):
        percent = "{0:.1f}".format(100 * (iteration / float(total)))
        filled_length = int(50 * iteration // total)
        bar = '=' * filled_length + ' ' * (50 - filled_length)
        print('\r%s |%s| %s%%' % (msg, bar, percent), end='\r')
        # Print New Line on Complete
        if iteration == total:
            print()

    def create_jail(self, jail_data: Jail, distribution: Distribution):
        if not self._jail_factory.base_jail_exists(distribution=distribution):
            if self._jail_factory.base_jail_incomplete(distribution=distribution):
                self._jail_factory.destroy_base_jail(distribution=distribution)

            with TemporaryDirectory(prefix="jmanager_", suffix="_tarballs") as temp_dir:
                path_to_temp_dir = PosixPath(temp_dir)
                self._http_fetcher.fetch_tarballs_into(distribution=distribution, temp_dir=path_to_temp_dir,
                                                       callback=JailManager.print_progress_bar)
                self._jail_factory.create_base_jail(distribution=distribution, path_to_tarballs=path_to_temp_dir)

        self._jail_factory.create_jail(jail_data=jail_data, os_version=distribution.version,
                                       architecture=distribution.architecture)

    def destroy_jail(self, jail_name: str):
        if self._jail_factory.jail_exists(jail_name):
            self._jail_factory.destroy_jail(jail_name)
        else:
            raise JailError(f"No jail named '{jail_name}'")

    def list_jails(self) -> List[Jail]:
        return self._jail_factory.list_jails()
