from rest_framework.test import APITestCase
from rest_framework import status
from pantry.models import TelegramUser

class TestCartAPI(APITestCase):
    def setUp(self):
        self.user = TelegramUser.objects.create(telegram_id=12345, username="test_user")

    def test_get_empty_cart(self):
        """Ensure we can retrieve a cart for a valid user, even if empty."""
        response = self.client.get('/api/cart/', {'user_id': 12345})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['items'], [])