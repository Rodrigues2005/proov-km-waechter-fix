# fleet_utils.py
# Catch-all helpers since 2013. Modernized 2025.
# Dead code (parse_service_date, chunk_list) removed.

MILES_PER_KM = 0.62137  # 1 km = 0.62137 miles  (was wrongly 1.609, which is km-per-mile)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a list; returns 0 for an empty list."""
    if not values:
        return 0
    return sum(values) / len(values)


def is_due(pct: float, threshold: float) -> bool:
    """Return True when pct is at or above threshold."""
    return pct >= threshold
