"""Exercise the real threaded HTTP server, not a mocked request handler."""
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from threading import Thread
import json
import unittest
from unittest.mock import patch

from services.api.app import Handler, ThreadingHTTPServer, reset_metrics


def samples(text):
    return {line.rsplit(" ", 1)[0]: float(line.rsplit(" ", 1)[1])
            for line in text.splitlines() if line and not line.startswith("#")}


class HttpServiceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        reset_metrics()

    def request(self, path):
        connection = HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            payload = response.read().decode()
            self.assertEqual(int(response.getheader("Content-Length")), len(payload.encode()))
            return response.status, response.getheader("Content-Type"), payload
        finally:
            connection.close()

    def test_work_success_and_failure_count_but_probes_do_not(self):
        self.assertEqual(self.request("/work?delay_ms=0")[0], 200)
        self.assertEqual(self.request("/work?delay_ms=0&fail=true")[0], 500)
        for _ in range(5):
            self.assertEqual(self.request("/healthz")[0], 200)
            self.assertEqual(self.request("/readyz")[0], 200)
            self.assertEqual(self.request("/missing")[0], 404)
        with patch.dict("os.environ", {"FORCE_NOT_READY": "true"}):
            self.assertEqual(self.request("/readyz")[0], 503)
        status, content_type, payload = self.request("/metrics")
        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/plain; version=0.0.4")
        values = samples(payload)
        self.assertEqual(values["demo_api_requests_total"], 2)
        self.assertEqual(values["demo_api_errors_total"], 1)
        self.assertEqual(values['demo_api_request_duration_seconds_bucket{le="+Inf"}'], 2)
        self.assertEqual(samples(self.request("/metrics")[2]), values)

    def test_invalid_delay_is_json_400_and_does_not_sleep_or_enter_slo(self):
        with patch("services.api.app.time.sleep") as sleep:
            for value in ("", "oops", "-1", "10001", "1.5", "nan", "inf", "1&delay_ms=2"):
                with self.subTest(value=value):
                    status, content_type, payload = self.request(f"/work?delay_ms={value}")
                    self.assertEqual(status, 400)
                    self.assertEqual(content_type, "application/json")
                    self.assertEqual(json.loads(payload)["status"], "invalid_request")
            sleep.assert_not_called()
        self.assertEqual(samples(self.request("/metrics")[2])["demo_api_requests_total"], 0)
        self.assertEqual(self.request("/work?delay_ms=0")[0], 200)

    def test_default_and_maximum_delay_are_supported(self):
        with patch("services.api.app.time.sleep") as sleep:
            self.assertEqual(json.loads(self.request("/work")[2])["delay_ms"], 25)
            self.assertEqual(json.loads(self.request("/work?delay_ms=10000")[2])["delay_ms"], 10000)
            self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.025, 10])

    def test_concurrent_http_work_has_consistent_histogram(self):
        def work(index):
            return self.request(f"/work?delay_ms=0&fail={'true' if index % 2 else 'false'}")[0]
        with ThreadPoolExecutor(max_workers=4) as pool:
            statuses = list(pool.map(work, range(80)))
        self.assertEqual(statuses.count(200), 40)
        self.assertEqual(statuses.count(500), 40)
        values = samples(self.request("/metrics")[2])
        self.assertEqual(values["demo_api_requests_total"], 80)
        self.assertEqual(values["demo_api_errors_total"], 40)
        self.assertEqual(values["demo_api_request_duration_seconds_count"], 80)
        self.assertEqual(values['demo_api_request_duration_seconds_bucket{le="+Inf"}'], 80)
        self.assertGreaterEqual(values["demo_api_request_duration_seconds_sum"], 0)
