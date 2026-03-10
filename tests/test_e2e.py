import json
import os
import subprocess
import sys
from pathlib import Path
import unittest


class TestE2E(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.report_path = self.project_root / "health_report.json"
        if self.report_path.exists():
            try:
                self.report_path.unlink()
            except Exception:
                pass

    def test_run_check_and_report(self):
        env = dict(os.environ)
        env.pop("SLACK_WEBHOOK_URL", None)  # ensure console fallback
        cmd = [sys.executable, str(self.project_root / "monitor.py"), "--check", "--quiet"]
        cp = subprocess.run(cmd, cwd=self.project_root, env=env, capture_output=True, text=True)
        # Допускаем любой код возврата; главное — корректное создание отчета
        self.assertIn(cp.returncode, (0, 1), msg=f"Process output:\n{cp.stdout}\n{cp.stderr}")
        self.assertTrue(self.report_path.exists(), "health_report.json not created")

        with self.report_path.open("r", encoding="utf-8") as f:
            report = json.load(f)
        self.assertIn("results", report)
        self.assertEqual(len(report["results"]), 4)

        results_by_name = {r["name"]: r for r in report["results"]}
        # Broken API should fail with 404
        broken = results_by_name.get("Broken API")
        self.assertIsNotNone(broken, "Broken API result missing")
        self.assertEqual(broken["status"], "failed")
        self.assertIn(broken["actual_status"], [404, None])


if __name__ == "__main__":
    unittest.main()
