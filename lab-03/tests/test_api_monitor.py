import socket
import ssl
import sys
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api_monitor import classify


class MonitorTests(unittest.TestCase):
    def test_error_categories(self):
        self.assertEqual(classify(urllib.error.URLError(socket.gaierror(-2, 'name not found'))), 'dns')
        self.assertEqual(classify(urllib.error.URLError(ConnectionRefusedError(111, 'refused'))), 'connection_refused')
        self.assertEqual(classify(urllib.error.URLError(TimeoutError('timed out'))), 'timeout')
        self.assertEqual(classify(urllib.error.URLError(ssl.SSLError('bad certificate'))), 'certificate_error')


if __name__ == '__main__':
    unittest.main()
