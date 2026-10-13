"""A burst of concurrent requests cannot exceed the process quota."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

from architect.review_quota import ReviewQuota


def test_concurrent_attempts_reserve_at_most_daily_limit():
    quota = ReviewQuota(20)
    today = date(2026, 10, 13)
    with ThreadPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(lambda _: quota.reserve(today), range(100)))
    assert sum(results) == 20
    assert not quota.reserve(today)
    assert quota.reserve(today + timedelta(days=1))
