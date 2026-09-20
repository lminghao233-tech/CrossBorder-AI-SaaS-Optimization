from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from core.benchmark import main as benchmark_main
from core.cost_router import main as router_main
from core.synthetic_data import write_json


class CliTests(unittest.TestCase):
    def test_router_cli(self):
        argv = ["cost-router", "--text", "Where is my parcel?", "--amount-usd", "50"]
        with patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()) as output:
            router_main()
        self.assertEqual(json.loads(output.getvalue())["route"], "economy")

    def test_benchmark_cli_outputs_files(self):
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "result.json"
            dataset_path = Path(directory) / "dataset.json"
            argv = [
                "benchmark", "--count", "30", "--output", str(result_path),
                "--dataset-output", str(dataset_path),
            ]
            with patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
                benchmark_main()
            self.assertEqual(json.loads(result_path.read_text())["sample_count"], 30)
            self.assertEqual(len(json.loads(dataset_path.read_text(encoding="utf-8"))), 30)

    def test_write_json(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "tickets.json"
            write_json(output, 3)
            self.assertEqual(len(json.loads(output.read_text(encoding="utf-8"))), 3)


if __name__ == "__main__":
    unittest.main()

