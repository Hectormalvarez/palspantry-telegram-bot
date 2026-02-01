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
            price_cents=1050,
            stock=100,
            description="Test description"
        )
        
        # Verify Product uses UUID for primary identifier
        self.assertIsInstance(product.id, uuid.UUID, 
                            "Product.id should be a UUID instance")
        
        # Verify Product has price_cents field for integer-based pricing
        self.assertTrue(hasattr(product, 'price_cents'), 
                       "Product should have price_cents field")
        
        # Verify price_cents is an integer type and equals 1050
        self.assertIsInstance(product.price_cents, int, 
                            "Product.price_cents should be an integer")
        self.assertEqual(product.price_cents, 1050,
                        "Product.price_cents should equal 1050")


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
            price_cents=1050,
            stock=100
        )
        
        # Create an order instance
        order = Order.objects.create(
            user=user,
            total_amount_cents=2100,
            status='pending'
        )
        
        # Verify Order uses UUID for primary identifier
        self.assertIsInstance(order.id, uuid.UUID, 
                            "Order.id should be a UUID instance")


class TestOrderArchitecture(TestCase):
    """Test cases for Order multi-item structure architecture."""
    
    def test_order_has_items_relationship(self):
        """Verify that Order can have a relationship to multiple OrderItem instances."""
        # Create a TelegramUser and two Products
        user = TelegramUser.objects.create(
            telegram_id=123456789,
            username="testuser",
            first_name="Test"
        )
        
        product1 = Product.objects.create(
            name="Product 1",
            price_cents=1000,
            stock=10
        )
        
        product2 = Product.objects.create(
            name="Product 2", 
            price_cents=2000,
            stock=20
        )
        
        # Attempt to create an Order without specifying a product (header only)
        order = Order.objects.create(
            user=user,
            status='pending'
        )
        
        # Import OrderItem inside the test method (will fail, which is expected)
        from pantry.models import OrderItem
        
        # Attempt to create two OrderItem instances linking the Order to the Products
        order_item1 = OrderItem.objects.create(
            order=order,
            product=product1,
            quantity=1,
            unit_price_cents=1050
        )
        
        order_item2 = OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=2,
            unit_price_cents=500
        )
        
        # Assert that the Order has a relationship to the items
        self.assertEqual(order.items.count(), 2)
        self.assertIn(order_item1, order.items.all())
        self.assertIn(order_item2, order.items.all())
