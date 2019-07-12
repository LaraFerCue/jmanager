import os
from pathlib import PosixPath
from tempfile import TemporaryDirectory, mkdtemp

from src.test.globals import remove_path


class TestGlobals:
    def test_remove_path_being_a_folder(self):
        temp_dir = mkdtemp()
        remove_path(PosixPath(temp_dir))
        assert not PosixPath(temp_dir).exists()

    def test_remove_path_being_a_file(self):
        with TemporaryDirectory() as temp_dir:
            open(f"{temp_dir}/file1", 'w').close()
            path_to_be_removed = PosixPath(temp_dir).joinpath('file1')
            remove_path(path_to_be_removed)

            assert not path_to_be_removed.exists()

    def test_remove_path_being_a_symlink(self):
        with TemporaryDirectory() as temp_dir:
            os.symlink('/dev/null', f"{temp_dir}/link")
            path_to_be_removed = PosixPath(temp_dir).joinpath('link')
            remove_path(path_to_be_removed)

            assert not path_to_be_removed.exists()
