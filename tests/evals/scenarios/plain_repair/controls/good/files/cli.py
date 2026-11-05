def parse_limit(text):
    value = int(text)
    if value < 0:
        raise ValueError("limit must not be negative")
    return value
