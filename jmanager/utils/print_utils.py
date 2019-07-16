def get_progress_text(msg: str, iteration: int, total: int) -> str:
    percent = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(50 * iteration // total)
    bar = '=' * filled_length + ' ' * (50 - filled_length)

    return "%s |%s| %s%%" % (msg, bar, percent)