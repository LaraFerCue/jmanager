import pytest

from src.utils.zfs import zfs_cmd, ZFSError


class TestZFS:
    def test_zfs_cmd(self):
        zfs_cmd(cmd="list", arguments=[], options={}, data_set='zroot')
        assert True

    def test_zfs_error(self):
        with pytest.raises(ZFSError):
            zfs_cmd(cmd='error', arguments=[], options={}, data_set='zroot')
