from typing import List

from models.architecture import Architecture
from models.version import Version


class Jail:
    def __init__(self, name: str, version: Version, architecture: Architecture, components: List[str]):
        self._name = name
        self._version = version
        self._components = components
        self._architecture = architecture

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> Version:
        return self._version

    @property
    def architecture(self) -> Architecture:
        return self._architecture

    @property
    def components(self) -> List[str]:
        return self._components
