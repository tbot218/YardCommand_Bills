from datetime import date, timedelta
import calendar
def fixed_day(year: int, month: int, day: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, last_day))
def nth_weekday(year: int, month: int, weekday: int, nth: int) -> date:
    first_day = date(year, month, 1)

    # move to first desired weekday
    days_ahead = (weekday - first_day.weekday()) % 7
    first_occurrence = first_day + timedelta(days=days_ahead)

    if nth == -1:
        # last weekday of month
        last_day = calendar.monthrange(year, month)[1]
        d = date(year, month, last_day)
        while d.weekday() != weekday:
            d -= timedelta(days=1)
        return d

    return first_occurrence + timedelta(days=7 * (nth - 1))
def first_business_day(year: int, month: int) -> date:
    d = date(year, month, 1)
    while d.weekday() >= 5:  # Sat/Sun
        d += timedelta(days=1)
    return d
