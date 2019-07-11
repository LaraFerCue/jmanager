import os

from models.jail import Jail
from src.test.globals import get_mocking_jail_factory, create_dummy_base_jail, destroy_dummy_jail, \
    destroy_dummy_base_jail, TEST_DISTRIBUTION


class TestJailFactoryStartStop:
    def test_start_jail(self):
        jail_factory = get_mocking_jail_factory()

        create_dummy_base_jail()
        try:
            jail_factory.create_jail(Jail('test'), TEST_DISTRIBUTION)
            mount_point_jail = jail_factory.base_jail_factory.get_jail_mountpoint('test')
            os.makedirs(mount_point_jail.joinpath('etc').as_posix())
            jail_factory.start_jail('test')

            assert mount_point_jail.joinpath('etc', 'resolv.conf').is_file()
        finally:
            destroy_dummy_jail('test')
            destroy_dummy_base_jail()

    def test_stop_jail(self):
        jail_factory = get_mocking_jail_factory()
        create_dummy_base_jail()
        try:
            jail_factory.create_jail(Jail('test'), TEST_DISTRIBUTION)
            jail_factory.stop_jail('test')
        finally:
            destroy_dummy_jail('test')
            destroy_dummy_base_jail()
