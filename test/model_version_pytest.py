import pytest

from models.version import Version, VersionType


class TestModelVersion:
    def test_create_version_from_string_with_right_data(self):
        version = Version.from_string("12.0-RELEASE")
        assert version.major == 12
        assert version.minor == 0
        assert version.version_type == VersionType.RELEASE

    def test_create_version_with_string_major_version(self):
        with pytest.raises(ValueError):
            Version.from_string("AA.0-RELEASE")

    def test_create_version_with_string_minor_version(self):
        with pytest.raises(ValueError):
            Version.from_string("12.AA-RELEASE")

    def test_create_version_with_unknown_version_type(self):
        with pytest.raises(ValueError):
            Version.from_string("12.0-UNKNOWN")
