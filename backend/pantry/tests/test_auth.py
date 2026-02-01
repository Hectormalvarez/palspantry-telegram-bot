from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from pantry.models import Product

@override_settings(INTERNAL_API_KEY='secret-key-123')
class TestAPIAuthentication(APITestCase):
    def setUp(self):
        # Create a product to ensure endpoints return data
        Product.objects.create(name="Test", price_cents=100, stock=10)

    def test_request_without_key_is_forbidden(self):
        """Requests without the X-API-KEY header should be rejected."""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_request_with_valid_key_is_accepted(self):
        """Requests with the correct key should succeed."""
        response = self.client.get(
            '/api/products/',
            headers={'X-API-KEY': 'secret-key-123'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_with_invalid_key_is_forbidden(self):
        """Requests with the wrong key should be rejected."""
        response = self.client.get(
            '/api/products/',
            headers={'X-API-KEY': 'wrong-key'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)