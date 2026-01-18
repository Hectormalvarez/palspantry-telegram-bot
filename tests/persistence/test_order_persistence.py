import pytest
from typing import Any  # For type hinting


@pytest.mark.asyncio
async def test_create_order_success(sqlite_persistence_layer):
    """Test successfully creating an order from cart items."""
    persistence = sqlite_persistence_layer

    # Arrange: Add a test product
    product_data = {
        "name": "Test Product",
        "price": 10.00,
        "quantity": 5,
        "category": "Test",
        "description": "Test product",
        "image_file_id": "test123",
    }
    product_id = await persistence.add_product(product_data)
    assert product_id is not None

    user_id = 123

    # Add 2 units of the product to the user's cart
    result = await persistence.add_to_cart(user_id, product_id, 2)
    assert result == 2

    # Act: Create the order
    order_id = await persistence.create_order(user_id)

    # Assert: Order ID is not None, and cart is empty
    assert order_id is not None
    cart_items = await persistence.get_cart_items(user_id)
    assert cart_items == {}


@pytest.mark.asyncio
async def test_get_order_details(sqlite_persistence_layer):
    """Test retrieving order details."""
    persistence = sqlite_persistence_layer

    # Setup: Create a product
    product_data = {
        "name": "Latte",
        "price": 4.50,
        "quantity": 10,
        "category": "Beverage",
        "description": "Delicious latte",
        "image_file_id": "latte123",
    }
    product_id = await persistence.add_product(product_data)
    assert product_id is not None

    user_id = 123

    # Action: Add 2 units of this product to the user's cart
    result = await persistence.add_to_cart(user_id, product_id, 2)
    assert result == 2

    # Action: Call persistence.create_order(123) to generate an order
    order_id = await persistence.create_order(user_id)
    assert order_id is not None

    # Action: Call persistence.get_order(order_id)
    order = await persistence.get_order(order_id)

    # Assertion: Verify the returned order object is not None
    assert order is not None

    # Assertion: Verify order["total_amount"] equals 9.0
    assert order["total_amount"] == 9.0

    # Assertion: Verify order["items"] contains the correct product name ("Latte") and quantity (2)
    items = order["items"]
    assert len(items) == 1
    item = items[0]
    assert item["name"] == "Latte"
    assert item["quantity"] == 2
