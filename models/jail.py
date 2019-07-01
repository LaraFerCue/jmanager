from typing import List

from models.version import Version


class Jail:
    def __init__(self, name: str, version: Version, architecture: str, components: List[str]):
        self._name = name
        self._version = version
        self._components = components
        self._architecture = architecture
