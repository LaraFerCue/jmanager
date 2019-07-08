from pathlib import PosixPath
from typing import Callable
from urllib.request import urlopen

from models.distribution import Distribution, Architecture, Version, VersionType


class HTTPFetcher:
    SERVER_URL = "http://ftp.FreeBSD.org"
    FTP_BASE_DIRECTORY = PosixPath('pub/FreeBSD')
    BLOCK_SIZE = 8192

    def fetch_file(self, url: str, destination: PosixPath, callback: Callable[[int, int], None] = None):
        fetcher = urlopen(url)
        file_size = int(fetcher.headers["content-length"])

        received_bytes = 0
        with open(destination.as_posix(), 'wb') as destination_file:
            while True:
                buffer = fetcher.read(self.BLOCK_SIZE)
                if not buffer:
                    break

                received_bytes += len(buffer)
                if callback is not None:
                    callback(received_bytes=received_bytes, total_bytes=file_size)
                destination_file.write(buffer)

    def fetch_tarballs_into(self, distribution: Distribution, temp_dir: PosixPath,
                            callback: Callable[[int, int], None] = None):
        directory = self.get_directory_path(distribution.architecture, distribution.version)
        base_url = f"{self.SERVER_URL}/{directory.as_posix()}"

        for component in distribution.components.copy():
            temp_file = temp_dir.joinpath(f"{component.value}.txz")
            self.fetch_file(url=f"{base_url}/{component.value}.txz", destination=temp_file, callback=callback)

    def get_directory_path(self, architecture: Architecture, version: Version) -> PosixPath:
        if version.version_type == VersionType.RELEASE:
            directory = self.FTP_BASE_DIRECTORY.joinpath('releases')
        else:
            directory = self.FTP_BASE_DIRECTORY.joinpath('snapshots')
        directory = directory.joinpath(architecture.value, str(version))
        return directory
