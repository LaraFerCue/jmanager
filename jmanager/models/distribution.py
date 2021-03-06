from enum import Enum
from pathlib import PosixPath
from typing import List

import yaml


class Architecture(Enum):
    AMD64 = "amd64"
    ARM = "arm"
    ARM64 = "arm64"
    I386 = "i386"
    POWERPC = "powerpc"
    SPARC64 = "sparc64"


class Component(Enum):
    MANIFEST = "MANIFEST"
    BASE_DEBUG = "base-dbg"
    BASE = "base"
    DOC = "doc"
    KERNEL_DEBUG = "kernel-dbg"
    KERNEL = "kernel"
    LIB32_DEBUG = "lib32-dbg"
    LIB32 = "lib32"
    PORTS = "ports"
    SRC = "src"
    TESTS = "tests"

    def __hash__(self):
        return hash(self.value)

    def __lt__(self, other: 'Component') -> bool:
        return self.value < other.value

    def __gt__(self, other: 'Component') -> bool:
        return not self <= other

    def __eq__(self, other: 'Component') -> bool:
        return self.value == other.value

    def __ne__(self, other: 'Component') -> bool:
        return not self == other

    def __le__(self, other: 'Component') -> bool:
        return self < other or self == other

    def __ge__(self, other: 'Component') -> bool:
        return self > other or self == other


class VersionType(Enum):
    RELEASE = "RELEASE"
    STABLE = "STABLE"
    CURRENT = "CURRENT"


class Version:
    def __init__(self, major: int, minor: int, version_type: VersionType):
        self._major = major
        self._minor = minor
        self._version_type = version_type

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    @property
    def version_type(self) -> VersionType:
        return self._version_type

    def __str__(self):
        return f"{self._major}.{self._minor}-{self._version_type.value}"

    @staticmethod
    def from_string(version: str):
        major_minor = version.split('-')[0].split('.')
        version_type = version.split('-')[1]

        return Version(int(major_minor[0]), int(major_minor[1]), VersionType(version_type))

    def __eq__(self, other: 'Version') -> bool:
        return self.major == other.major and self.minor == other.minor and self.version_type == other.version_type

    def __ne__(self, other: 'Version') -> bool:
        return not self.__eq__(other)


class Distribution:
    def __init__(self, version: Version, architecture: Architecture, components: List[Component]):
        self._version = version
        self._components = components.copy()
        if Component.BASE not in self._components:
            self._components.append(Component.BASE)
        self._components.sort()
        self._architecture = architecture

    @property
    def version(self) -> Version:
        return self._version

    @property
    def architecture(self) -> Architecture:
        return self._architecture

    @property
    def components(self) -> List[Component]:
        return self._components

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        components = [component.value for component in self.components]
        return f"{self.version}/{self.architecture.value}/{components}"

    def __eq__(self, other: 'Distribution') -> bool:
        is_equal = self.version == other.version and self.architecture == other.architecture
        return is_equal and set(self.components) == set(other.components)

    def __ne__(self, other: 'Distribution') -> bool:
        return not self.__eq__(other)

    def write_config_file(self, path_to_file: PosixPath):
        configuration = {
            'version': str(self.version),
            'architecture': self.architecture.value,
            'components': [comp.value for comp in self.components]
        }
        with open(path_to_file.as_posix(), 'w') as config_file:
            yaml.dump(configuration, stream=config_file)

    @staticmethod
    def read_config_file(path_to_config_file: PosixPath) -> 'Distribution':
        with open(path_to_config_file.as_posix(), 'r') as config_file:
            configuration = yaml.load(stream=config_file, Loader=yaml.Loader)

        components = [Component(comp) for comp in configuration['components']]
        return Distribution(
            version=Version.from_string(configuration['version']),
            architecture=Architecture(configuration['architecture']),
            components=components
        )
