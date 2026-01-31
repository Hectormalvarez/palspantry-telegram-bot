import pytest
from typing import Any  # For type hinting


def _create_sample_product_data(
    name="Milk",
    price=2.99,
    quantity=10,
    category="Dairy",
    description="Fresh milk",
    image_file_id="img123",
) -> dict[str, Any]:
    return {
        "name": name,
        "price": price,
        "quantity": quantity,
        "category": category,
        "description": description,
        "image_file_id": image_file_id,
    }


@pytest.mark.asyncio
async def test_add_to_cart_and_retrieve(sqlite_persistence_layer):
    """Test adding an item to the cart and retrieving it."""
    persistence = sqlite_persistence_layer

    # Add a product to have a product_id
    product_data = _create_sample_product_data()
    product_id = await persistence.add_product(product_data)
    assert product_id is not None

    user_id = 123

    # Initially, cart should be empty
    cart_items = await persistence.get_cart_items(user_id)
    assert cart_items == {}

    # Add item to cart
    result = await persistence.add_to_cart(user_id, product_id, 1)
    assert result == 1

    # Retrieve cart items
    cart_items = await persistence.get_cart_items(user_id)
    assert cart_items == {product_id: 1}


@pytest.mark.asyncio
async def test_update_cart_quantity(sqlite_persistence_layer):
    """Test updating cart quantity by adding the same item again."""
    persistence = sqlite_persistence_layer

    # Add a product to have a product_id
    product_data = _create_sample_product_data()
    product_id = await persistence.add_product(product_data)
    assert product_id is not None

    user_id = 456

    # Add item to cart initially
    result = await persistence.add_to_cart(user_id, product_id, 1)
    assert result == 1

    # Check initial cart
    cart_items = await persistence.get_cart_items(user_id)
    assert cart_items == {product_id: 1}

    # Add the same item again (should increment quantity)
    result = await persistence.add_to_cart(user_id, product_id, 1)
    assert result == 2

    # Check updated cart
    cart_items = await persistence.get_cart_items(user_id)
    assert cart_items == {product_id: 2}  # 1 + 1 = 2


@pytest.mark.asyncio
async def test_clear_cart(sqlite_persistence_layer):
    """Test clearing the cart after adding items."""
    persistence = sqlite_persistence_layer

    # Add two products
    product_data1 = _create_sample_product_data(name="Milk")
    product_data2 = _create_sample_product_data(name="Bread", category="Bakery")
    product_id1 = await persistence.add_product(product_data1)
    product_id2 = await persistence.add_product(product_data2)
    assert product_id1 is not None
    assert product_id2 is not None

    user_id = 789

    # Add items to cart
    result1 = await persistence.add_to_cart(user_id, product_id1, 2)
    result2 = await persistence.add_to_cart(user_id, product_id2, 1)
    assert result1 == 2
    assert result2 == 1

    # Verify items are in cart
    cart_items = await persistence.get_cart_items(user_id)
    assert cart_items == {product_id1: 2, product_id2: 1}

    # Clear the cart
    cleared = await persistence.clear_cart(user_id)
    assert cleared is True

    # Verify cart is empty
    cart_items = await persistence.get_cart_items(user_id)
    assert cart_items == {}
