from collections import deque
from threading import Lock


class PerformanceMetrics:
    def __init__(self, max_samples=500):
        self._durations_ms = deque(maxlen=max_samples)
        self._status_codes = deque(maxlen=max_samples)
        self._lock = Lock()

    def record(self, duration_ms, status_code):
        with self._lock:
            self._durations_ms.append(duration_ms)
            self._status_codes.append(status_code)

    def get_average_response_time_ms(self):
        with self._lock:
            if not self._durations_ms:
                return 0
            return sum(self._durations_ms) / len(self._durations_ms)

    def get_error_rate_percentage(self):
        with self._lock:
            total = len(self._status_codes)
            if total == 0:
                return 0
            errors = sum(1 for code in self._status_codes if code >= 500)
            return (errors / total) * 100


_metrics = PerformanceMetrics()


def get_performance_metrics():
    return _metrics
