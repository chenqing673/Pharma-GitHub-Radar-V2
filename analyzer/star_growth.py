def growth_rate(current, previous):
    if previous == 0:
        return current

    return round((current - previous) / previous * 100, 2)
