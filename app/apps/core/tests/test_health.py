from django.test import TestCase, Client
from django.urls import reverse


class HealthEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_endpoint_ok(self):
        resp = self.client.get('/health/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode('utf-8'), 'OK')
