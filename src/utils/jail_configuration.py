from pathlib import PosixPath


def configure_ssh_service_configuration_file(path_to_config_file: PosixPath, jail_port: int):
    with open(path_to_config_file.as_posix(), 'a') as config_file:
        config_file.write(f'ListenAddress localhost:{jail_port}\n')


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
