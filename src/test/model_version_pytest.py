import pytest

from models.distribution import Version, VersionType


class TestModelVersion:
    def test_create_version_from_string_with_right_data(self):
        version = Version.from_string("12.0-RELEASE")
        assert version.major == 12
        assert version.minor == 0
        assert version.version_type == VersionType.RELEASE

    def test_create_version_with_string_major_version(self):
        with pytest.raises(ValueError, match=r"invalid literal for int\(\) with base 10: 'Major'"):
            Version.from_string("Major.0-RELEASE")

    def test_create_version_with_string_minor_version(self):
        with pytest.raises(ValueError, match=r"invalid literal for int\(\) with base 10: 'Minor'"):
            Version.from_string("12.Minor-RELEASE")

    def test_create_version_with_unknown_version_type(self):
        with pytest.raises(ValueError, match=r"'UNKNOWN' is not a valid VersionType"):
            Version.from_string("12.0-UNKNOWN")

    def test_version_equality(self):
        version1 = Version(12, 0, VersionType.RELEASE)
        version2 = Version(12, 0, VersionType.RELEASE)
        version3 = Version(11, 0, VersionType.RELEASE)
        version4 = Version(12, 1, VersionType.RELEASE)
        version5 = Version(12, 0, VersionType.STABLE)
        version6 = Version(11, 1, VersionType.RELEASE)
        version7 = Version(12, 1, VersionType.STABLE)
        version8 = Version(11, 1, VersionType.STABLE)

        assert version1 == version2
        assert version1 != version3
        assert version1 != version4
        assert version1 != version5
        assert version1 != version6
        assert version1 != version7
        assert version1 != version8
