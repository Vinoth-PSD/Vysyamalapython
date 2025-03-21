from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status

class ChangePasswordTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='old_password')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('change-password')

    def test_change_password_success(self):
        data = {
            'old_password': 'old_password',
            'new_password': 'new_password',
            'confirm_password': 'new_password',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))

    def test_change_password_wrong_old_password(self):
        data = {
            'old_password': 'wrong_old_password',
            'new_password': 'new_password',
            'confirm_password': 'new_password',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        data = {
            'old_password': 'old_password',
            'new_password': 'new_password',
            'confirm_password': 'different_new_password',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
