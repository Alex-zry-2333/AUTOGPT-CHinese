from datetime import datetime


def get_datetime() -> str:
    """Return the current date and time

    Returns:
        str: The current date and time
    """
    return "当前日期与时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
