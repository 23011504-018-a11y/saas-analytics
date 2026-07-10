import json
import subprocess
import unittest
from pathlib import Path

from app import app


ROOT = Path(__file__).resolve().parent
PYTHON = Path(ROOT / ".venv" / "Scripts" / "python.exe")


class AnalyzeSaasTests(unittest.TestCase):
    def test_sample_dataset_generates_outputs(self):
        result = subprocess.run(
            [
                str(PYTHON),
                str(ROOT / "analyze_saas.py"),
                str(ROOT / "sample_saas_data.csv"),
                "--as-of-date",
                "2024-10-01",
                "--output-dir",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("customers_total", result.stdout)

        metrics_path = ROOT / "saas_metrics.json"
        self.assertTrue(metrics_path.exists())
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        self.assertEqual(metrics["customers_total"], 6)
        self.assertEqual(metrics["mrr"], 530.0)

    def test_dashboard_renders_without_python_booleans(self):
        client = app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("SaaS Analytics Dashboard", html)
        self.assertNotIn("True", html)
        self.assertNotIn("False", html)


if __name__ == "__main__":
    unittest.main()
