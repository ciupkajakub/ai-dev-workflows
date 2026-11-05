from pricing import format_price


def total_for(values):
    return sum(float(format_price(value)) for value in values)
