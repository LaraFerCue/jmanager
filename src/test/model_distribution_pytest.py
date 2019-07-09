from models.distribution import Distribution, Version, VersionType, Architecture, Component


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
