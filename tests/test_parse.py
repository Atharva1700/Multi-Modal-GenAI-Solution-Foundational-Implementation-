import unittest

from main import parse_json_response


class ParseJsonResponseTests(unittest.TestCase):
    def test_plain_json(self):
        self.assertEqual(parse_json_response('{"title": "A"}'), {"title": "A"})

    def test_fenced_json(self):
        self.assertEqual(parse_json_response('```json\n{"title": "B"}\n```'), {"title": "B"})


if __name__ == "__main__":
    unittest.main()
