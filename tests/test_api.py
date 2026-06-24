import unittest

from services.api.app import ERROR_COUNT, REQUEST_COUNT, metrics_text, observe_request, reset_metrics


class ApiMetricsTest(unittest.TestCase):
    def setUp(self):
        reset_metrics()

    def test_metrics_include_prometheus_counters(self):
        observe_request(0.05, 200)
        text = metrics_text()
        self.assertIn("demo_api_requests_total 1", text)
        self.assertIn("demo_api_errors_total 0", text)

    def test_error_count_increments_for_5xx(self):
        observe_request(0.2, 500)
        text = metrics_text()
        self.assertIn("demo_api_errors_total 1", text)

    def test_reset_metrics_clears_state(self):
        observe_request(0.2, 500)
        reset_metrics()
        self.assertIn("demo_api_requests_total 0", metrics_text())


if __name__ == "__main__":
    unittest.main()
