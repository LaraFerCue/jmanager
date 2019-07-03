import subprocess
from enum import Enum
from typing import List, Dict


class ZFSError(BaseException):
    pass


class ZFSType(Enum):
    FILESYSTEM = "filesystem"
    SNAPSHOT = "snapshot"
    VOLUME = "volume"
    BOOKMARK = "bookmark"
    ALL = "all"


class ZFSProperty(Enum):
    NAME = "NAME"
    USED = "USED"
    AVAIL = "AVAIL"
    REFER = "REFER"
    MOUNTPOINT = "MOUNTPOINT"


def zfs_cmd(cmd: str, arguments: List[str], options: Dict[str, str], data_set: str):
    for option, value in options.items():
        arguments.append('-o')
        arguments.append(f"{option}={value}")
    try:
        out = subprocess.run(' '.join(['zfs', cmd, *arguments, data_set]), shell=True, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as error:
        raise ZFSError(error) from error

    return out.stdout


def zfs_create(data_set: str, options: Dict[str, str]):
    zfs_cmd(cmd='create', arguments=['-p'], options=options, data_set=data_set)


def zfs_list(data_set: str = "", depth: int = 0, exact_numbers: bool = False,
             properties: List[ZFSProperty] = (), types: List[ZFSType] = (), sort_by: List[ZFSProperty] = (),
             sort_by_reversed: List[ZFSProperty] = ()) -> List[Dict[ZFSProperty, str]]:
    """
    Lists the dataset given as an argument
    :param data_set: The dataset whose information is to be retrieved.
    :param depth: Indicates if only the dataset is to be shown, all children or just upto some depth.
    :param exact_numbers: Get information using exact numbers.
    :param properties: Only display the given properties.
    :param types: Only retrieve information for the given type of datasets.
    :param sort_by: Sort the entries by this properties.
    :param sort_by_reversed: Sort the entries in reverse order by this properties.

    :return: A dictionary containing properties retrieved by the command.
    """
    output = zfs_cmd(cmd='list', arguments=['-H'], options={}, data_set=data_set)

    if properties == ():
        properties = (ZFSProperty.NAME, ZFSProperty.USED, ZFSProperty.AVAIL, ZFSProperty.REFER, ZFSProperty.MOUNTPOINT)

    zfs_data_sets = []
    for line in output.split('\n'):
        if not line:
            break
        data_set: Dict[ZFSProperty, str] = {}
        data = line.split('\t')
        for i in range(0, len(properties)):
            data_set[properties[i]] = data[i]
        zfs_data_sets.append(data_set)
    return zfs_data_sets
