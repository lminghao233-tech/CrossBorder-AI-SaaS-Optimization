import unittest

from core.pii_masker import mask_pii


class PiiMaskerTests(unittest.TestCase):
    def test_masks_email(self):
        result = mask_pii("Contact jane@example.com")
        self.assertIn("[EMAIL_1]", result.text)
        self.assertNotIn("jane@example.com", result.text)

    def test_masks_phone(self):
        result = mask_pii("Call +86 138-0013-8000")
        self.assertIn("[PHONE_1]", result.text)

    def test_masks_order(self):
        result = mask_pii("Track order #ABC-12345")
        self.assertIn("[ORDER_1]", result.text)

    def test_keeps_mapping_in_result(self):
        result = mask_pii("Email a@b.com")
        self.assertEqual(result.replacements["[EMAIL_1]"], "a@b.com")


if __name__ == "__main__":
    unittest.main()

