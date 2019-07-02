from enum import Enum


class VersionType(Enum):
    RELEASE = "RELEASE"
    STABLE = "STABLE"
    CURRENT = "CURRENT"


class Version:
    def __init__(self, major: int, minor: int, version_type: VersionType):
        self._major = major
        self._minor = minor
        self._type = version_type

    def __str__(self):
        return f"{self._major}.{self._minor}-{self._type.value}"

    @staticmethod
    def from_string(version: str):
        major_minor = version.split('-')[0].split('.')
        version_type = version.split('-')[1]

        return Version(int(major_minor[0]), int(major_minor[1]), VersionType(version_type))
