import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from log_analyzer import analyze, parse_line


class LogTests(unittest.TestCase):
    def test_valid_and_invalid(self):
        line = '192.0.2.1 - - [13/Oct/2026:10:04:20 +0000] "GET / HTTP/1.1" 200 25 "-" "agent"'
        self.assertEqual(parse_line(line)['status'], 200)
        self.assertIsNone(parse_line('invalid row'))
        report = analyze([line, 'broken', line], 3)
        self.assertEqual(report['malformed_lines'], 1)
        self.assertEqual(report['top_ips'][0]['requests'], 2)


if __name__ == '__main__':
    unittest.main()
