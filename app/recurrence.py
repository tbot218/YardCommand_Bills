from datetime import date, timedelta
import calendar
from typing import Union, Dict


# ============================================================
# DATE HELPERS
# ============================================================

def fixed_day(year: int, month: int, day: int) -> date:
    """
    Return a date clamped to the last valid day of the month.
    Example: Feb 30 → Feb 28/29
    """
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, last_day))


def nth_weekday(
    year: int,
    month: int,
    weekday: int,
    nth: int,
) -> date:
    """
    Return the nth weekday of a month.

    weekday: 0=Mon ... 6=Sun
    nth:
        1..4  → first, second, third, fourth
        -1    → last weekday of month
    """

    if not 0 <= weekday <= 6:
        raise ValueError("weekday must be between 0 (Mon) and 6 (Sun)")

    first_day = date(year, month, 1)

    days_ahead = (weekday - first_day.weekday()) % 7
    first_occurrence = first_day + timedelta(days=days_ahead)

    if nth == -1:
        last_dom = calendar.monthrange(year, month)[1]
        d = date(year, month, last_dom)
        while d.weekday() != weekday:
            d -= timedelta(days=1)
        return d

    if nth < 1:
        raise ValueError("nth must be >= 1 or -1")

    result = first_occurrence + timedelta(days=7 * (nth - 1))

    if result.month != month:
        raise ValueError("Requested nth weekday does not exist in this month")

    return result


def first_business_day(year: int, month: int) -> date:
    """
    Return the first weekday (Mon–Fri) of the month.
    """
    d = date(year, month, 1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def last_business_day(year: int, month: int) -> date:
    """
    Return the last weekday (Mon–Fri) of the month.
    """
    last_dom = calendar.monthrange(year, month)[1]
    d = date(year, month, last_dom)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def _add_month(d: date) -> date:
    """
    Safely advance a date by one calendar month.
    """
    month = d.month + 1
    year = d.year

    if month > 12:
        month = 1
        year += 1

    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


# ============================================================
# OCCURRENCE ENGINE
# ============================================================

def _next_occurrence(
    current: date,
    recurrence: Union[str, Dict],
) -> date:
    """
    Calculate the next occurrence date.

    recurrence may be:
    - str: "weekly", "fortnightly", "monthly", "yearly"
    - dict: advanced monthly rules
    """

    # -------------------------
    # SIMPLE STRING RULES
    # -------------------------
    if isinstance(recurrence, str):

        if recurrence == "weekly":
            return current + timedelta(weeks=1)

        if recurrence == "fortnightly":
            return current + timedelta(weeks=2)

        if recurrence == "monthly":
            return _add_month(current)

        if recurrence == "yearly":
            return date(current.year + 1, current.month, current.day)

        raise ValueError(f"Unknown recurrence: {recurrence}")

    # -------------------------
    # ADVANCED RULES
    # -------------------------
    if isinstance(recurrence, dict):

        rtype = recurrence.get("type")

        if rtype == "monthly":
            next_month = _add_month(current)
            mode = recurrence.get("mode")

            if mode == "fixed_day":
                return fixed_day(
                    next_month.year,
                    next_month.month,
                    recurrence["day"],
                )

            if mode == "nth_weekday":
                return nth_weekday(
                    next_month.year,
                    next_month.month,
                    recurrence["weekday"],
                    recurrence["nth"],
                )

            if mode == "first_business_day":
                return first_business_day(
                    next_month.year,
                    next_month.month,
                )

            if mode == "last_business_day":
                return last_business_day(
                    next_month.year,
                    next_month.month,
                )

            raise ValueError(f"Unknown monthly mode: {mode}")

        raise ValueError(f"Unknown recurrence type: {rtype}")

    raise TypeError("recurrence must be str or dict")

from typing import List, Dict


def expand_bills_to_instances(
    bills: List[Dict],
    start_date: date,
    end_date: date,
) -> List[Dict]:
    """
    Expand recurring bill rules into dated bill instances
    between start_date and end_date (inclusive).

    Each returned instance:
    {
        "bill_id": int,
        "date": date,
        "amount": float,
        "user": str,
    }
    """

    instances: List[Dict] = []

    for bill in bills:
        current = bill["start_date"]

        # Skip bills that start after the window
        if current > end_date:
            continue

        # Advance to the first occurrence >= start_date
        while current < start_date:
            current = _next_occurrence(current, bill["recurrence"])

        # Generate instances within the window
        while current <= end_date:
            instances.append({
                "bill_id": bill["id"],
                "date": current,
                "amount": bill["amount"],
                "user": bill.get("user", "default"),
            })

            current = _next_occurrence(current, bill["recurrence"])

    return instances
