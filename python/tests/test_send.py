"""Request-shape checks. Run from python/: python -m unittest discover -s tests"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import mailhuset  # noqa: E402


class FakeClient(mailhuset.Mailhuset):
    def __init__(self) -> None:
        super().__init__("mh_test_x")
        self.calls = []

    def _request(self, method, path, body=None):
        self.calls.append((method, path, body))
        return {"id": "msg_1", "status": "queued"}


class SendTests(unittest.TestCase):
    def test_send_passes_tracking(self) -> None:
        mh = FakeClient()
        mh.emails.send(sender="a@example.com", to="b@example.com", subject="Hi",
                       tracking={"opens": True, "clicks": False})
        method, path, body = mh.calls[0]
        self.assertEqual((method, path), ("POST", "/email"))
        self.assertEqual(body["tracking"], {"opens": True, "clicks": False})
        self.assertEqual(body["to"], ["b@example.com"])

    def test_send_omits_unset_tracking(self) -> None:
        mh = FakeClient()
        mh.emails.send(sender="a@example.com", to="b@example.com", subject="Hi")
        self.assertNotIn("tracking", mh.calls[0][2])

    def test_batch_passes_tracking_per_message(self) -> None:
        mh = FakeClient()
        mh.emails.batch([
            {"sender": "a@example.com", "to": "b@example.com", "tracking": {"clicks": True}},
            {"sender": "a@example.com", "to": "c@example.com"},
        ])
        messages = mh.calls[0][2]["messages"]
        self.assertEqual(messages[0]["tracking"], {"clicks": True})
        self.assertNotIn("tracking", messages[1])


if __name__ == "__main__":
    unittest.main()
