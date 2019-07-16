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


class ZFS:
    ZFS_CLI = "zfs"

    def zfs_cmd(self, cmd: str, arguments: List[str], options: Dict[str, str], data_set: str):
        for option, value in options.items():
            arguments.append('-o')
            arguments.append(f"{option}={value}")
        try:
            out = subprocess.run(' '.join([self.ZFS_CLI, cmd, *arguments, data_set]), shell=True, check=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as error:
            raise ZFSError(error) from error

        return out.stdout

    def zfs_create(self, data_set: str, options: Dict[str, str]):
        self.zfs_cmd(cmd='create', arguments=['-p'], options=options, data_set=data_set)

    def zfs_destroy(self, data_set: str, arguments: List[str] = ()):
        self.zfs_cmd(cmd='destroy', arguments=['-f', *arguments], options={}, data_set=data_set)

    def zfs_snapshot(self, data_set: str, snapshot_name: str, options: Dict[str, str] = None, recursive: bool = False):
        zfs_arguments = []
        if recursive:
            zfs_arguments.append('-r')

        if options is None:
            options = {}
        self.zfs_cmd(cmd="snapshot", arguments=zfs_arguments, options=options, data_set=f"{data_set}@{snapshot_name}")

    def zfs_list(self, data_set: str = "", depth: int = 0, properties: List[ZFSProperty] = (),
                 types: List[ZFSType] = (), arguments: List[str] = ()) -> List[Dict[ZFSProperty, str]]:
        """
        Lists the dataset given as an argument
        :param data_set: The dataset whose information is to be retrieved.
        :param depth: Indicates if only the dataset is to be shown, all children or just upto some depth.
        :param properties: Only display the given properties.
        :param types: Only retrieve information for the given type of datasets.
        :param arguments: Extra arguments for the command.

        :return: A dictionary containing properties retrieved by the command.
        """
        if properties == ():
            properties = (ZFSProperty.NAME, ZFSProperty.USED, ZFSProperty.AVAIL,
                          ZFSProperty.REFER, ZFSProperty.MOUNTPOINT)
        zfs_arguments = ['-H', *arguments]
        if depth < 0:
            zfs_arguments.append('-r')
        elif depth > 0:
            zfs_arguments.extend(['-d', str(depth)])

        zfs_types = ','.join([x.value for x in types])
        if zfs_types:
            zfs_arguments.extend(['-t', zfs_types])

        try:
            output = self.zfs_cmd(cmd='list', arguments=zfs_arguments, options={}, data_set=data_set)
        except ZFSError:
            return []

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

    def zfs_clone(self, snapshot: str, data_set: str, options: Dict[str, str]):
        self.zfs_cmd(cmd='clone', data_set=f"{snapshot} {data_set}", options=options, arguments=['-p'])

    def zfs_get(self, data_set: str, depth: int = 0,
                properties: List[str] = ()) -> Dict[str, Dict[str, str]]:
        zfs_arguments = ['-H']
        if depth < 0:
            zfs_arguments.append('-r')
        else:
            zfs_arguments.extend(['-d', str(depth)])

        if not properties:
            zfs_arguments.append('all')
        else:
            zfs_arguments.extend(properties)
        output = self.zfs_cmd(cmd='get', arguments=zfs_arguments, options={}, data_set=data_set)

        options_dictionary: Dict[str, Dict[str, str]] = {}
        for line in output.split('\n'):
            if not line:
                break
            data = line.split('\t')
            if data[0] not in options_dictionary.keys():
                options_dictionary[data[0]] = {}
            options_dictionary[data[0]][data[1]] = data[2]
        return options_dictionary
