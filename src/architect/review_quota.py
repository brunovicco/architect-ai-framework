"""Process-local request reservation for the optional shared reviewer."""
from datetime import date
from threading import Lock


class ReviewQuota:
    """Reserve attempts atomically; failed requests still consume budget.

    This is a process-local guard, not a distributed or persistent quota.
    Restarts reset it; enforce a spending ceiling at the provider as well.
    """

    def __init__(self, daily_limit: int) -> None:
        self.daily_limit = daily_limit
        self._date: date | None = None
        self._count = 0
        self._lock = Lock()

    def reserve(self, today: date) -> bool:
        with self._lock:
            if self._date != today:
                self._date = today
                self._count = 0
            if self._count >= self.daily_limit:
                return False
            self._count += 1
            return True
