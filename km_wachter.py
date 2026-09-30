# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Modernized 2025.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return how much of the service interval has been used, as a percentage."""
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True when the car has used at least WARN_AT_PERCENT of its service interval.

    Cars with no last_service_km reading are treated as freshly serviced (km_since = 0)
    so they are never falsely flagged.
    """
    last = car.get("last_service_km", car["odometer"])
    km_since = car["odometer"] - last
    return wear_percent(km_since, SERVICE_INTERVAL_KM) >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list[str]:
    """Flag every car that needs a service and return the list of their IDs."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
