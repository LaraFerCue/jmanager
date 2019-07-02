from pathlib import PosixPath
from tempfile import TemporaryDirectory

from models.architecture import Architecture
from models.jail import Jail
from models.version import Version, VersionType
from src.fetch_utils import fetch_tarballs_into


class TestFetchUtils:
    def test_fetch_base_tarball(self):
        jail_version = Version(major=12, minor=0, version_type=VersionType.RELEASE)
        jail = Jail(name='name', version=jail_version, architecture=Architecture.AMD64, components=[])

        with TemporaryDirectory() as temp_dir:
            temp_dir_path = PosixPath(temp_dir)
            fetch_tarballs_into(jail, temp_dir_path)
            assert temp_dir_path.joinpath('base.txz').is_file()
