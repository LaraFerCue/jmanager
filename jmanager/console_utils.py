from jmanager.utils.print_utils import get_progress_text


def print_progress_bar_extract(msg: str, iteration: int, total: int):
    progress_text = get_progress_text(msg, iteration, total)

    print('\r%s ' % progress_text, end='\r')
    if iteration == total:
        print()


def print_progress_bar_fetch(msg, iteration, total, speed):
    progress_text = get_progress_text(msg, iteration, total)

    print('\r%s %2.2f Mbps  ' % (progress_text, speed / 1e6), end='\r')
    if iteration == total:
        print()
