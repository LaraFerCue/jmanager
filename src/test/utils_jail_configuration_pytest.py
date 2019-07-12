from pathlib import PosixPath
from tempfile import TemporaryDirectory

from src.utils.jail_configuration import configure_ssh_service_configuration_file, configure_services, \
    create_private_key, write_public_key


class TestJailConfiguration:
    def test_sshd_configuration(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = PosixPath(temp_dir)
            configure_ssh_service_configuration_file(temp_dir_path.joinpath('sshd_config'), jail_port=2201)

            with open(temp_dir_path.joinpath('sshd_config').as_posix(), 'r') as sshd_config:
                assert sshd_config.read() == "ListenAddress localhost:2201\nPermitRootLogin yes\n"

    def test_editing_services(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = PosixPath(temp_dir)
            configure_services(temp_dir_path.joinpath('rc.conf'))

            with open(temp_dir_path.joinpath('rc.conf').as_posix(), 'r') as rc_conf:
                assert rc_conf.read() == "sshd_enable=\"YES\"\n"

    def test_editing_services_with_service_already_active(self):
        with TemporaryDirectory() as temp_dir:
            with open(f"{temp_dir}/rc.conf", 'w') as config_file:
                config_file.write('sshd_enable="YES"\n')

            temp_dir_path = PosixPath(temp_dir)
            configure_services(temp_dir_path.joinpath('rc.conf'))

            with open(temp_dir_path.joinpath('rc.conf').as_posix(), 'r') as rc_conf:
                assert rc_conf.read() == "sshd_enable=\"YES\"\n"

    def test_editing_services_with_service_inactive(self):
        with TemporaryDirectory() as temp_dir:
            with open(f"{temp_dir}/rc.conf", 'w') as config_file:
                config_file.write('sshd_enable="NO"\n')

            temp_dir_path = PosixPath(temp_dir)
            configure_services(temp_dir_path.joinpath('rc.conf'))

            with open(temp_dir_path.joinpath('rc.conf').as_posix(), 'r') as rc_conf:
                assert rc_conf.read() == "sshd_enable=\"YES\"\n"

    def test_editing_services_with_other_content(self):
        with TemporaryDirectory() as temp_dir:
            with open(f"{temp_dir}/rc.conf", 'w') as config_file:
                config_file.write('sshd_enable="NO"\n')
                config_file.write('other_service_enable="YES"\n')

            temp_dir_path = PosixPath(temp_dir)
            configure_services(temp_dir_path.joinpath('rc.conf'))

            with open(temp_dir_path.joinpath('rc.conf').as_posix(), 'r') as rc_conf:
                assert rc_conf.read() == "other_service_enable=\"YES\"\nsshd_enable=\"YES\"\n"

    def test_write_private_key(self):
        with TemporaryDirectory() as temp_dir:
            create_private_key(PosixPath(temp_dir).joinpath('priv.key'))
            assert PosixPath(temp_dir).joinpath('priv.key').is_file()

    def test_write_public_key(self):
        with TemporaryDirectory() as temp_dir:
            priv_key_path = PosixPath(temp_dir).joinpath('priv.key')
            pub_key_path = PosixPath(temp_dir).joinpath('pub.key')
            create_private_key(priv_key_path)

            write_public_key(priv_key_path, pub_key_path)
            assert pub_key_path.is_file()
