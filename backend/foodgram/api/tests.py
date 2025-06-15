from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class APISmokeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_api_root_exists(self):
        response = self.client.get('/api/')
        self.assertIn(response.status_code, [200, 301, 302], "API root не доступен")

