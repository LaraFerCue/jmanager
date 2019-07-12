import os
from os import stat
from pathlib import PosixPath
from stat import UF_HIDDEN
from tempfile import TemporaryDirectory

from src.utils.file_utils import set_flags_to_folder_recursively


def create_immutable_folder(temp_dir: str):
    open(f"{temp_dir}/file1", 'w').close()
    open(f"{temp_dir}/file2", 'w').close()
    open(f"{temp_dir}/file3", 'w').close()
    os.chflags(f"{temp_dir}/file1", UF_HIDDEN)
    os.chflags(f"{temp_dir}/file2", UF_HIDDEN)
    os.chflags(f"{temp_dir}/file3", UF_HIDDEN)


def assert_folder_mutable(temp_dir: str):
    assert not stat(f"{temp_dir}/file1").st_flags & UF_HIDDEN


class TestFileUtils:

    def test_make_folder_mutable_only_files(self):
        with TemporaryDirectory() as temp_dir:
            create_immutable_folder(temp_dir)
            set_flags_to_folder_recursively(path=PosixPath(temp_dir), flags=not UF_HIDDEN)

            assert_folder_mutable(temp_dir)

    def test_make_folder_mutable_with_symlinks(self):
        with TemporaryDirectory() as temp_dir:
            create_immutable_folder(temp_dir)
            os.symlink(f"{temp_dir}/file1", f"{temp_dir}/link")
            set_flags_to_folder_recursively(path=PosixPath(temp_dir), flags=not UF_HIDDEN)

            assert_folder_mutable(temp_dir)

    def test_make_folder_mutable_with_sub_folders(self):
        with TemporaryDirectory() as temp_dir:
            create_immutable_folder(temp_dir)
            os.makedirs(f"{temp_dir}/sub_dir")
            create_immutable_folder(f"{temp_dir}/sub_dir")

            set_flags_to_folder_recursively(path=PosixPath(temp_dir), flags=not UF_HIDDEN)
            assert_folder_mutable(f"{temp_dir}/sub_dir")
            assert_folder_mutable(temp_dir)
