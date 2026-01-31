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
        
        # Verify price_cents exists and is an int (this will cause AttributeError)
        self.assertIsInstance(product.price_cents, int, 
                            "Product.price_cents should exist and be an int")


class TestTelegramUserModel(TestCase):
    """Test cases for TelegramUser model schema requirements."""
    
    def test_telegram_user_schema(self):
        """Verify that the TelegramUser model uses UUID for primary identifier and integer for telegram_id."""
        # Create a TelegramUser instance
        user = TelegramUser.objects.create(
            telegram_id=123456789,
            username="testuser",
            first_name="Test"
        )
        
        # Verify TelegramUser uses UUID for primary identifier
        self.assertIsInstance(user.id, uuid.UUID, 
                            "TelegramUser.id should be a UUID instance")
        
        # Verify TelegramUser has telegram_id field as integer
        self.assertIsInstance(user.telegram_id, int, 
                            "TelegramUser.telegram_id should be an integer")
    
    def test_telegram_id_uniqueness(self):
        """Verify that attempting to create two users with the same telegram_id raises IntegrityError."""
        # Create first user
        TelegramUser.objects.create(
            telegram_id=123456789,
            username="testuser1",
            first_name="Test1"
        )
        
        # Attempt to create second user with same telegram_id
        from django.db.utils import IntegrityError
        
        with self.assertRaises(IntegrityError):
            TelegramUser.objects.create(
                telegram_id=123456789,  # Same telegram_id
                username="testuser2",
                first_name="Test2"
            )


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
