from rest_framework.test import APITestCase
from rest_framework import status
from pantry.models import TelegramUser, Product, CartItem, Order

class TestOrderAPI(APITestCase):
    def setUp(self):
        self.user = TelegramUser.objects.create(telegram_id=12345, username="test_user")
        self.product = Product.objects.create(name="Coffee", price_cents=500, stock=10)
        # Add items to cart
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)

    def test_checkout_flow(self):
        """Test valid checkout: Cart -> Order -> Response -> Cleanup."""
        payload = {'user_id': 12345}
        response = self.client.post('/api/orders/', data=payload)

        # 1. Assert Response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['total_amount_cents'], 1000)

        # 2. Assert Database State
        # Cart should be empty
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)
        # Order should exist
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_amount_cents, 1000)
        # Order items should exist
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().unit_price_cents, 500)