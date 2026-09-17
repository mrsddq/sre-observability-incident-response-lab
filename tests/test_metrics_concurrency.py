from concurrent.futures import ThreadPoolExecutor
from threading import Event
import unittest

from services.api.app import metrics_text, observe_request, reset_metrics


def samples(text):
    return {line.rsplit(" ", 1)[0]: float(line.rsplit(" ", 1)[1])
            for line in text.splitlines() if line and not line.startswith("#")}


class HistogramContractTest(unittest.TestCase):
    def setUp(self):
        reset_metrics()

    def test_histogram_buckets_are_cumulative_and_sum_includes_all_durations(self):
        for duration in (0.1, 0.2, 0.5, 1.5):
            observe_request(duration, 200)
        values = samples(metrics_text())
        for bound, count in (("0.1", 1), ("0.3", 2), ("0.5", 3), ("1.0", 3), ("+Inf", 4)):
            self.assertEqual(values[f'demo_api_request_duration_seconds_bucket{{le="{bound}"}}'], count)
        self.assertEqual(values["demo_api_request_duration_seconds_count"], 4)
        self.assertAlmostEqual(values["demo_api_request_duration_seconds_sum"], 2.3)
        reset_metrics()
        self.assertEqual(samples(metrics_text())["demo_api_request_duration_seconds_sum"], 0)

    def test_scrapes_observe_atomic_snapshots_while_writers_are_active(self):
        start = Event()
        def writer():
            start.wait(timeout=5)
            for _ in range(2000):
                observe_request(0.05, 500)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(writer) for _ in range(4)]
            start.set()
            for _ in range(250):
                values = samples(metrics_text())
                count = values["demo_api_requests_total"]
                self.assertEqual(values["demo_api_errors_total"], count)
                self.assertEqual(values["demo_api_request_duration_seconds_count"], count)
                self.assertEqual(values['demo_api_request_duration_seconds_bucket{le="+Inf"}'], count)
            for future in futures:
                future.result(timeout=5)
        self.assertEqual(samples(metrics_text())["demo_api_requests_total"], 8000)
