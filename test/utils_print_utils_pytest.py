from jmanager.utils.print_utils import get_progress_text

PROGRESS_TEXT = "test |=========================                         | 50.0%"


class TestPrintUtils:
    def test_get_progress_text(self):
        assert get_progress_text(msg="test", iteration=1, total=2) == PROGRESS_TEXT
