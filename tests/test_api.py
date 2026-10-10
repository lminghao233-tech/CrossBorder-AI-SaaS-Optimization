import unittest

from fastapi.testclient import TestClient

from core.api import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        self.assertEqual(self.client.get("/health").json()["status"], "ok")

    def test_resolve(self):
        response = self.client.post(
            "/v1/support/resolve",
            json={"text": "请查询订单 ABC-12345 的物流", "request_id": "api-test"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["request_id"], "api-test")
        self.assertTrue(response.json()["grounded"])

    def test_negative_amount_is_rejected(self):
        response = self.client.post(
            "/v1/support/resolve", json={"text": "parcel", "amount_usd": -1}
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
