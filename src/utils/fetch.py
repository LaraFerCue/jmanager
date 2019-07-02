from ftplib import FTP
from pathlib import PosixPath

from models.jail import Jail, Architecture, Component, Version, VersionType

SERVER_URL = "ftp.FreeBSD.org"
FTP_BASE_DIRECTORY = PosixPath('pub/FreeBSD')


def fetch_tarballs_into(jail_info: Jail, temp_dir: PosixPath):
    ftp_connector = FTP(SERVER_URL)
    ftp_connector.login()

    directory = get_directory_path(jail_info.architecture, jail_info.version)
    ftp_connector.cwd(directory.as_posix())

    components = jail_info.components.copy()
    components.append(Component.BASE)

    for component in components:
        temp_file = temp_dir.joinpath(f"{component.value}.txz").as_posix()
        ftp_connector.retrbinary(f"RETR {component.value}.txz", open(temp_file, 'wb').write)

    ftp_connector.quit()


def get_directory_path(architecture: Architecture, version: Version):
    if version.version_type == VersionType.RELEASE:
        directory = FTP_BASE_DIRECTORY.joinpath('releases')
    else:
        directory = FTP_BASE_DIRECTORY.joinpath('snapshots')
    directory = directory.joinpath(architecture.value, str(version))
    return directory
