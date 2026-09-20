import unittest

from core.cost_router import CostRouter, RouteRequest


class RouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = CostRouter()

    def test_routine_goes_to_economy(self):
        result = self.router.route(RouteRequest("Where is my parcel?"))
        self.assertEqual(result.route, "economy")

    def test_high_risk_goes_to_premium_and_review(self):
        result = self.router.route(RouteRequest("We face a contract breach"))
        self.assertEqual(result.route, "premium")
        self.assertTrue(result.require_human_review)

    def test_high_amount_overrides_routine(self):
        result = self.router.route(RouteRequest("Where is my parcel?", 2_000))
        self.assertEqual(result.reason, "high-amount-hard-rule")

    def test_unknown_falls_back_to_premium(self):
        result = self.router.route(RouteRequest("Please handle this"))
        self.assertEqual(result.reason, "low-confidence-fallback")

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValueError):
            self.router.route(RouteRequest("parcel", -1))

    def test_empty_text_rejected(self):
        with self.assertRaises(ValueError):
            self.router.route(RouteRequest("  "))

    def test_output_contains_masked_text(self):
        result = self.router.route(RouteRequest("parcel for order #ABC-12345"))
        self.assertNotIn("ABC-12345", result.masked_text)


if __name__ == "__main__":
    unittest.main()

