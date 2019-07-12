from typing import List, Dict

from models.distribution import Distribution, Version, Architecture, Component
from models.jail import Jail, JailParameter


class JManagerFile:
    def __init__(self, jail_name: str, version: Version, architecture: Architecture,
                 components: List[Component] = (), jail_parameters: Dict[JailParameter, str] = None):
        self._distribution = Distribution(version=version, architecture=architecture, components=components)
        self._jail = Jail(name=jail_name, parameters=jail_parameters)

    @property
    def distribution(self) -> Distribution:
        return self._distribution

    @property
    def jail(self) -> Jail:
        return self._jail
