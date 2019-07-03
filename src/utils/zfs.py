import subprocess
from typing import List, Dict


class ZFSError(BaseException):
    pass


def zfs_cmd(cmd: str, arguments: List[str], options: Dict[str, str], data_set: str):
    for option, value in options.items():
        arguments.append('-o')
        arguments.append(f"{option}={value}")
    try:
        subprocess.run(' '.join(['zfs', cmd, *arguments, data_set]), shell=True, check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as error:
        raise ZFSError(error) from error


def zfs_create(data_set: str, options: Dict[str, str]):
    zfs_cmd(cmd='create', arguments=['-p'], options=options, data_set=data_set)
