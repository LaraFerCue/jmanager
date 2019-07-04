from typing import List

from models.distribution import Distribution, Version, Architecture, Component
from models.jail import Jail


class JManagerFile:
    def __init__(self, name: str, version: Version, architecture: Architecture, components: List[Component]):
        self._distribution = Distribution(version=version, architecture=architecture, components=components)
        self._jail = Jail(name=name)

    @property
    def distribution(self) -> Distribution:
        return self._distribution

    @property
    def jail(self) -> Jail:
        return self._jail
