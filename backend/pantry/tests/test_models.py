import uuid
from django.test import TestCase
from pantry.models import Product, Order, TelegramUser


class TestProductModel(TestCase):
    """Test cases for Product model schema requirements."""
    
    def test_product_schema_requirements(self):
        """Verify that the Product model uses UUID for primary identifier and integer for price_cents."""
        # Create a product instance
        product = Product.objects.create(
            name="Test Product",
            price=10.50,
            stock=100,
            description="Test description"
        )
        
        # Verify Product uses UUID for primary identifier
        self.assertIsInstance(product.id, uuid.UUID, 
                            "Product.id should be a UUID instance")
        
        # Verify Product has price_cents field for integer-based pricing
        self.assertTrue(hasattr(product, 'price_cents'), 
                       "Product should have price_cents field")
        
        # Verify price_cents is an integer type
        self.assertIsInstance(product.price_cents, int, 
                            "Product.price_cents should be an integer")


class TestOrderModel(TestCase):
    """Test cases for Order model schema requirements."""
    
    def test_order_schema_parity(self):
        """Verify that the Order model uses UUID for primary identifier to maintain schema consistency."""
        # Create required related instances
        user = TelegramUser.objects.create(
            telegram_id=123456789,
            username="testuser",
            first_name="Test"
        )
        
        product = Product.objects.create(
            name="Test Product",
            price=10.50,
            stock=100
        )
        
        # Create an order instance
        order = Order.objects.create(
            user=user,
            product=product,
            quantity=2,
            status='pending'
        )
        
        # Verify Order uses UUID for primary identifier
        self.assertIsInstance(order.id, uuid.UUID, 
                            "Order.id should be a UUID instance")
