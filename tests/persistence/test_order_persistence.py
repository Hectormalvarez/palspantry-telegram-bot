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
