from datetime import date
from typing import Dict, List
from collections import defaultdict


def compute_weekly_totals(instances: List[Dict]) -> Dict[str, float]:
    """
    Aggregate instances into ISO weekly totals.
    Key format: YYYY-Www (e.g., 2025-W03)
    """
    totals = defaultdict(float)

    for inst in instances:
        d: date = inst["date"]
        amount: float = inst["amount"]

        year, week, _ = d.isocalendar()
        key = f"{year}-W{week:02d}"
        totals[key] += amount

    return dict(totals)


def compute_monthly_totals(instances: List[Dict]) -> Dict[str, float]:
    """
    Aggregate instances into calendar monthly totals.
    Key format: YYYY-MM (e.g., 2025-01)
    """
    totals = defaultdict(float)

    for inst in instances:
        d: date = inst["date"]
        amount: float = inst["amount"]

        key = f"{d.year}-{d.month:02d}"
        totals[key] += amount

    return dict(totals)
