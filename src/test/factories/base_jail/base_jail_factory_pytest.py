import shutil

import pytest

from src.test.globals import get_mocking_base_jail_factory, TMP_PATH

TEST_JAIL_NAME = "test"


class TestBaseJailFactory:
    def test_jail_factory_jail_path_do_not_exist(self):
        if TMP_PATH.exists():
            if TMP_PATH.is_dir():
                shutil.rmtree(TMP_PATH.as_posix())
            else:
                TMP_PATH.unlink()
        get_mocking_base_jail_factory(TMP_PATH)
        assert TMP_PATH.is_dir()

    def test_jail_factory_jail_path_is_a_file(self):
        if TMP_PATH.exists():
            shutil.rmtree(TMP_PATH.as_posix(), ignore_errors=True)
        open(TMP_PATH.as_posix(), 'w').close()

        with pytest.raises(PermissionError, match=r"The jail root path exists and it is not a directory"):
            get_mocking_base_jail_factory(TMP_PATH)
        TMP_PATH.unlink()
