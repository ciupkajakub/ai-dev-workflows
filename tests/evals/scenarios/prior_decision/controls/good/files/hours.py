from datetime import timedelta

WINDOW_DAYS = 30


def is_active(last_log, today):
    return today - timedelta(days=WINDOW_DAYS) <= last_log <= today


def remaining_hours(budget, used):
    return budget - used
