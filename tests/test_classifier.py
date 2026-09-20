import unittest

from core.classifier import IntentClassifier, detect_language


class ClassifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.classifier = IntentClassifier()

    def test_detects_english(self):
        self.assertEqual(detect_language("Where is my parcel?"), "en")

    def test_detects_chinese(self):
        self.assertEqual(detect_language("查询物流"), "zh")

    def test_detects_korean(self):
        self.assertEqual(detect_language("배송 조회"), "ko")

    def test_logistics_intent(self):
        result = self.classifier.classify("Where is my parcel?")
        self.assertEqual((result.intent, result.risk), ("logistics", "routine"))

    def test_legal_intent_is_high_risk(self):
        result = self.classifier.classify("This is a contract breach lawsuit")
        self.assertEqual((result.intent, result.risk), ("legal_dispute", "high"))

    def test_unknown_is_low_confidence(self):
        result = self.classifier.classify("Please help with this")
        self.assertEqual(result.intent, "unknown")
        self.assertLess(result.confidence, 0.6)

    def test_risk_wins_a_tie(self):
        result = self.classifier.classify("parcel lawsuit")
        self.assertEqual(result.intent, "legal_dispute")


if __name__ == "__main__":
    unittest.main()

