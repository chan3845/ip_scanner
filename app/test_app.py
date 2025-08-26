import unittest
import json
import tempfile
import os
from unittest.mock import patch
from app import app, load_cidrs, save_cidrs

class NetworkScannerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Create a temporary file for CIDRs
        self.temp_cidr_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.temp_cidr_file.write("[]")  # Write an empty JSON list
        self.temp_cidr_file.flush() 
        self.addCleanup(os.unlink, self.temp_cidr_file.name)

        # Patch CIDR_FILE globally for each test
        patcher = patch("app.CIDR_FILE", self.temp_cidr_file.name)
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Network Scanner', response.data)   # header exists
        self.assertIn(b'Manage Networks', response.data)


    def test_manage_route_get(self):
        response = self.app.get('/manage')
        self.assertEqual(response.status_code, 200)

    def test_manage_route_post_add(self):
        response = self.app.post('/manage', data={'action': 'add', 'cidr': '192.168.1.0/24'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with open(self.temp_cidr_file.name, 'r') as f:
            cidrs = json.load(f)
        self.assertIn('192.168.1.0/24', cidrs)

    def test_manage_route_post_delete(self):
        save_cidrs(['192.168.1.0/24'])  # prepopulate file
        response = self.app.post('/manage', data={'action': 'delete', 'cidr': '192.168.1.0/24'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with open(self.temp_cidr_file.name, 'r') as f:
            cidrs = json.load(f)
        self.assertNotIn('192.168.1.0/24', cidrs)

    def test_scan_route(self):
        response = self.app.get('/scan/127.0.0.1/32')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("ips", data)
        self.assertIn("scan_time", data)

    def test_invalid_cidr_scan(self):
        response = self.app.get('/scan/invalid_cidr')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid CIDR', response.data)

    def test_load_cidrs(self):
        expected = ["192.168.1.0/24", "10.0.0.0/24"]
        with open(self.temp_cidr_file.name, 'w') as f:
            json.dump(expected, f)

        result = load_cidrs()
        self.assertEqual(result, expected)

    def test_save_cidrs(self):
        test_data = ["192.168.1.0/24", "10.0.0.0/24", "172.16.0.0/24"]
        save_cidrs(test_data)
        with open(self.temp_cidr_file.name, 'r') as f:
            result = json.load(f)
        self.assertEqual(result, test_data)

if __name__ == '__main__':
    unittest.main()

