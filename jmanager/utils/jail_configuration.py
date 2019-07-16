from pathlib import PosixPath

from paramiko import rsakey


def configure_ssh_service_configuration_file(path_to_config_file: PosixPath, jail_port: int):
    with open(path_to_config_file.as_posix(), 'a') as config_file:
        config_file.write(f'ListenAddress localhost:{jail_port}\n')
        config_file.write('PermitRootLogin yes\n')


def configure_services(service_configure_file_path: PosixPath):
    content = []

    if service_configure_file_path.is_file():
        with open(service_configure_file_path.as_posix(), 'r') as service_config_file:
            for line in service_config_file.readlines():
                if line.startswith('sshd_enable="YES"'):
                    return

                if not line.startswith('sshd_enable='):
                    content.append(line)

    with open(service_configure_file_path.as_posix(), 'w') as service_config_file:
        service_config_file.write('\n'.join(content))
        service_config_file.write('sshd_enable="YES"\n')


def create_private_key(priv_key_file_path: PosixPath):
    priv_key = rsakey.RSAKey.generate(4096)
    priv_key.write_private_key_file(priv_key_file_path.as_posix())


def write_public_key(priv_key_path: PosixPath, pub_key_path: PosixPath):
    priv_key = rsakey.RSAKey.from_private_key_file(priv_key_path.as_posix())

    with open(pub_key_path.as_posix(), 'w') as pub_key_file:
        pub_key_file.write(
            "%(key_type)s %(key_content)s %(username)s@%(hostname)s" % {
                'key_type': priv_key.get_name(),
                'key_content': priv_key.get_base64(),
                'username': 'jmanager',
                'hostname': 'localhost',
            }
        )


def read_port_from_config_file(config_file_path: PosixPath) -> int:
    with open(config_file_path.as_posix(), 'r') as config_file:
        for line in config_file.readlines():
            if line.startswith('ListenAddress'):
                return int(line.split()[1].split(':')[1])
    return -1
