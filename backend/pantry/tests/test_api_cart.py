from rest_framework.test import APITestCase
from rest_framework import status
from pantry.models import TelegramUser, Product

class TestCartAPI(APITestCase):
    def setUp(self):
        self.user = TelegramUser.objects.create(telegram_id=12345, username="test_user")
        self.product = Product.objects.create(name="Test Coffee", price_cents=500, stock=10)

    def test_get_empty_cart(self):
        """Ensure we can retrieve a cart for a valid user, even if empty."""
        response = self.client.get('/api/cart/', {'user_id': 12345})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['items'], [])

    def test_add_item_to_cart(self):
        """Ensure we can add an item to the cart."""
        payload = {'product_id': self.product.id, 'quantity': 2, 'user_id': 12345}
        response = self.client.post('/api/cart/', data=payload)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
        self.assertEqual(response.data['items'][0]['product']['name'], "Test Coffee")
        self.assertEqual(response.data['items'][0]['quantity'], 2)
