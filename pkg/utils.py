def formatted_time(seconds: int) -> str:
    """
    Converting seconds to hours minutes seconds

    :param seconds: Number of seconds
    :return: Formatted string in time format
    """
    hour = seconds // 3600
    seconds = seconds % 3600
    minutes = seconds // 60
    seconds = seconds % 60
    if hour != 0 and minutes != 0 and seconds != 0:
        return f'{hour}h {minutes}m {seconds}s'
    if minutes != 0 and seconds != 0:
        return f'{minutes}m {seconds}s'
    if seconds == 0:
        return '0.1s'
    return f'{seconds}s'
