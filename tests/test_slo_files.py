import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SloFilesTest(unittest.TestCase):
    def test_runbooks_exist_for_alerts(self):
        alerts = (ROOT / "observability" / "prometheus" / "alerts.yml").read_text(encoding="utf-8")
        self.assertIn("runbooks/error-rate.md", alerts)
        self.assertIn("runbooks/high-latency.md", alerts)
        self.assertTrue((ROOT / "runbooks" / "error-rate.md").exists())
        self.assertTrue((ROOT / "runbooks" / "high-latency.md").exists())

    def test_slo_mentions_error_budget(self):
        slo = (ROOT / "slo" / "demo-api.yaml").read_text(encoding="utf-8")
        self.assertIn("error_budget_policy", slo)
        self.assertIn("99.9", slo)


if __name__ == "__main__":
    unittest.main()
