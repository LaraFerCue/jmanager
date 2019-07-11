import lzma
import shutil
import tarfile
from os import chflags
from pathlib import PosixPath
from stat import SF_IMMUTABLE
from tempfile import TemporaryDirectory
from typing import Callable


def extract_tarball_into(jail_path: PosixPath, path_to_tarball: PosixPath,
                         callback: Callable[[str, int, int], None]):
    with TemporaryDirectory(prefix="jail_factory_") as temp_dir:
        temp_file_path = f"{temp_dir}/{path_to_tarball.name}"
        with lzma.open(path_to_tarball.as_posix(), 'r') as lz_file:
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(lz_file.read())

        msg = f"Extracting {path_to_tarball.name}"
        with tarfile.open(temp_file_path, mode='r') as tar_file:
            members = tar_file.getmembers()
            iteration = 0
            for member in members:
                if callback is not None:
                    callback(msg, iteration, len(members))
                tar_file.extract(member, path=jail_path.as_posix())
                iteration += 1
            if callback is not None:
                callback(msg, len(members), len(members))


def make_folder_content_mutable(path: PosixPath, recursive: bool = False):
    if not path.is_dir() and not path.is_symlink():
        chflags(path.as_posix(), not SF_IMMUTABLE)
        return

    if not recursive or path.is_symlink():
        return

    for node in path.iterdir():
        make_folder_content_mutable(path=node, recursive=recursive)


def remove_immutable_path(jail_path: PosixPath):
    make_folder_content_mutable(jail_path, True)
    shutil.rmtree(jail_path, ignore_errors=True)