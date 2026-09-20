import unittest

from core.benchmark import PRICES, request_cost, run_benchmark
from core.synthetic_data import generate_tickets


class BenchmarkTests(unittest.TestCase):
    def test_generation_is_deterministic(self):
        self.assertEqual(generate_tickets(20), generate_tickets(20))

    def test_all_records_are_marked_synthetic(self):
        self.assertTrue(all(item.synthetic for item in generate_tickets(20)))

    def test_invalid_count_rejected(self):
        with self.assertRaises(ValueError):
            generate_tickets(0)

    def test_premium_cost_is_higher(self):
        economy = request_cost(PRICES["economy"], 100, 100)
        premium = request_cost(PRICES["premium"], 100, 100)
        self.assertGreater(premium, economy)

    def test_benchmark_sample_count(self):
        self.assertEqual(run_benchmark(100)["sample_count"], 100)

    def test_high_risk_is_never_sent_to_economy(self):
        self.assertEqual(run_benchmark(600)["high_risk_premium_recall"], 1.0)

    def test_cost_reduction_is_reproducible(self):
        result = run_benchmark(600)
        self.assertGreater(result["modeled_cost_reduction"], 0.30)
        self.assertLess(result["modeled_cost_reduction"], 0.33)


if __name__ == "__main__":
    unittest.main()

