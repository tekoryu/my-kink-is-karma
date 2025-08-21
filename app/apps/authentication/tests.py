from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User


class AuthenticationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('authentication:login')
        # Create a user for authentication tests
        self.user = User.objects.create_user(username='admin', password='secret123')

    def test_login_success(self):
        payload = {"username": "admin", "password": "secret123"}
        resp = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', resp.data)
        self.assertEqual(resp.data['username'], 'admin')

    def test_login_invalid_credentials(self):
        payload = {"username": "admin", "password": "wrong"}
        resp = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', resp.data)

    def test_login_missing_credentials(self):
        payload = {"username": "admin"}
        resp = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', resp.data)
