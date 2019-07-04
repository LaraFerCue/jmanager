from enum import Enum
from typing import List


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


class Distribution:
    def __init__(self, version: Version, architecture: Architecture, components: List[Component]):
        self._version = version
        self._components = [Component.BASE, *components]
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
