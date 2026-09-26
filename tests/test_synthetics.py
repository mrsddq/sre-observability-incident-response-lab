import unittest
from unittest.mock import patch

from synthetics.check_http import check


class SyntheticCheckTest(unittest.TestCase):
    def test_socket_timeout_returns_failed_observation(self):
        with patch("synthetics.check_http.urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            ok, elapsed, status = check("http://127.0.0.1/healthz", 0.01)
        self.assertFalse(ok)
        self.assertIsNone(status)
        self.assertGreaterEqual(elapsed, 0)
