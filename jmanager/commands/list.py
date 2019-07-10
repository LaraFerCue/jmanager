from enum import Enum

from jmanager.jail_manager import JailManager

LIST_HEADER = "JAIL\tBASE JAIL"
BASE_JAIL_HEADER = "VERSION\t\tARCH\tCOMPONENTS"


class ListType(Enum):
    JAILS = 'jail'
    BASE_JAILS = 'base'


def print_list_of_base_jails(jail_manager: JailManager):
    print(BASE_JAIL_HEADER)
    for distribution in jail_manager.list_base_jails():
        components = ', '.join([component.value for component in distribution.components])
        print(f"{distribution.version}\t{distribution.architecture.value}\t{components}")


def list_command(list_type: str, jail_manager: JailManager):
    type_to_list = ListType(list_type)
    if type_to_list == ListType.JAILS:
        print_list_of_jails(jail_manager)
    elif type_to_list == ListType.BASE_JAILS:
        print_list_of_base_jails(jail_manager)


def print_list_of_jails(jail_manager: JailManager):
    print(LIST_HEADER)
    for jail in jail_manager.list_jails():
        components = ','.join([component.value for component in jail.origin.components])
        print(f"{jail.name}\t{jail.origin.version} / {jail.origin.architecture.value} ({components})")
