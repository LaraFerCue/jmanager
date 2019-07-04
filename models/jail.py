from enum import Enum
from typing import Dict


class JailOption(Enum):
    pass


class Jail:
    def __init__(self, name: str, options: Dict[JailOption, str] = None):
        self._name = name
        self._options = {}
        if options is not None:
            self._options.update(options)

    @property
    def name(self) -> str:
        return self._name

    @property
    def options(self) -> Dict[JailOption, str]:
        return self._options
