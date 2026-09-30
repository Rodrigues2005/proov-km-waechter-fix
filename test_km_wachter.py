# test_km_wachter.py
from km_wachter import needs_service, wear_percent, WARN_AT_PERCENT, SERVICE_INTERVAL_KM


def test_almost_due_car_is_flagged():
    # A car at 14,900 of its 15,000 km window is about 99% worn and MUST be flagged.
    assert needs_service({"id": "VOS-4471", "odometer": 14900, "last_service_km": 0}) is True


def test_missing_reading_is_not_treated_as_zero():
    # A car with NO last-service reading must not be treated as fully worn.
    assert needs_service({"id": "VOS-7788", "odometer": 92000}) is False


def test_wear_percent_uses_float_division():
    # 14,900 of 15,000 km is 99.33…% — integer floor division would wrongly give 0%.
    pct = wear_percent(14900, SERVICE_INTERVAL_KM)
    assert 99.0 <= pct <= 100.0


def test_wear_percent_below_threshold_not_flagged():
    # 11,999 km of 15,000 is 79.99% — just below WARN_AT_PERCENT (80), so not due.
    pct = wear_percent(11999, SERVICE_INTERVAL_KM)
    assert pct < WARN_AT_PERCENT


def test_wear_percent_at_threshold_is_flagged():
    # Exactly 80% (12,000 km of 15,000) must trigger the warning.
    pct = wear_percent(12000, SERVICE_INTERVAL_KM)
    assert pct >= WARN_AT_PERCENT
    assert needs_service({"id": "VOS-0001", "odometer": 12000, "last_service_km": 0}) is True


def test_warn_at_percent_is_80():
    # The 80% threshold must remain untouched.
    assert WARN_AT_PERCENT == 80


def test_service_interval_is_15000():
    # The 15,000 km interval must remain untouched.
    assert SERVICE_INTERVAL_KM == 15000
