from pathlib import PosixPath

from jmanager.jail_manager import JailManager
from src.configuration import parse_jmanagerfile, read_configuration_file


def create_command(jmanagerfile: str, jail_manager: JailManager):
    jmanagerfile_path = PosixPath(jmanagerfile)
    jmanagerfile_list = parse_jmanagerfile(read_configuration_file(jmanagerfile_path))

    for jmanagerfile in jmanagerfile_list:
        jail_manager.create_jail(jail_data=jmanagerfile.jail, distribution=jmanagerfile.distribution)
        jail_manager.start(jail_name=jmanagerfile.jail.name)
        jail_manager.provision_jail(jail_name=jmanagerfile.jail.name, provision_dict={})
