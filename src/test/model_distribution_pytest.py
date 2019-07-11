import filecmp
from pathlib import PosixPath
from tempfile import TemporaryDirectory

from models.distribution import Distribution, Version, VersionType, Architecture, Component
from src.test.globals import TEST_DISTRIBUTION


class TestModelDistribution:
    def test_distribution_equality(self):
        version1 = Version(12, 0, VersionType.STABLE)
        version2 = Version(11, 0, VersionType.STABLE)

        dist1 = Distribution(version=version1, architecture=Architecture.AMD64, components=[])
        dist2 = Distribution(version=version1, architecture=Architecture.AMD64, components=[])
        dist3 = Distribution(version=version1, architecture=Architecture.I386, components=[])
        dist4 = Distribution(version=version2, architecture=Architecture.AMD64, components=[])
        dist5 = Distribution(version=version1, architecture=Architecture.AMD64,
                             components=[Component.LIB32])
        dist6 = Distribution(version=version2, architecture=Architecture.I386, components=[])
        dist7 = Distribution(version=version1, architecture=Architecture.I386,
                             components=[Component.LIB32])
        dist8 = Distribution(version=version2, architecture=Architecture.I386,
                             components=[Component.LIB32])

        assert dist1 == dist2
        assert dist1 != dist3
        assert dist1 != dist4
        assert dist1 != dist5
        assert dist1 != dist6
        assert dist1 != dist7
        assert dist1 != dist8

    def test_distribution_representation(self):
        assert str(TEST_DISTRIBUTION) == "12.0-RELEASE/amd64/['base']"

    def test_distribution_hash(self):
        assert hash(TEST_DISTRIBUTION) == hash("12.0-RELEASE/amd64/['base']")

    def test_components_inequality(self):
        comp1 = Component.KERNEL

        assert comp1 > Component.BASE
        assert comp1 != Component.BASE
        assert Component.BASE <= comp1 <= Component.KERNEL
        assert Component.SRC >= comp1 >= Component.KERNEL

    def test_write_configuration(self):
        with TemporaryDirectory() as temp_dir:
            TEST_DISTRIBUTION.write_config_file(PosixPath(temp_dir).joinpath('test'))

            assert filecmp.cmp(f"{temp_dir}/test", "src/test/resources/dist.conf", shallow=False)
