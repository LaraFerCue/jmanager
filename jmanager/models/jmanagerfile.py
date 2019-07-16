from pathlib import PosixPath
from tempfile import mkstemp
from typing import List, Dict, Any

import yaml

from jmanager.models.distribution import Distribution, Version, Architecture, Component
from jmanager.models.jail import Jail, JailParameter


class JManagerFile:
    def __init__(self, jail_name: str, version: Version, architecture: Architecture,
                 components: List[Component] = (), jail_parameters: Dict[JailParameter, str] = None,
                 provision: Dict[str, Any] = None):
        self._distribution = Distribution(version=version, architecture=architecture, components=components)
        self._jail = Jail(name=jail_name, parameters=jail_parameters)

        if provision is not None:
            if provision['type'] == 'inline':
                _, temp_file_path = mkstemp()
                final_provision = [{'tasks': provision['provision'], 'hosts': jail_name}]
                with open(temp_file_path, 'w') as temp_file:
                    yaml.dump(final_provision, stream=temp_file)

                self._provision_file_path = PosixPath(temp_file_path)
            elif provision['type'] == 'file':
                if 'path' not in provision:
                    raise AttributeError("Path is a mandatory option for the provision type 'file'")
                self._provision_file_path = PosixPath(provision['path'])

                if not self._provision_file_path.is_file():
                    raise FileNotFoundError(f"Provision file {self._provision_file_path.as_posix()} is missing")
            else:
                raise ValueError(f"Wrong value '{provision['type']}' for provision type")
        else:
            self._provision_file_path = None

    @property
    def distribution(self) -> Distribution:
        return self._distribution

    @property
    def jail(self) -> Jail:
        return self._jail

    @property
    def provision_file_path(self) -> PosixPath:
        return self._provision_file_path
