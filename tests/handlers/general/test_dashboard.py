import pytest
from unittest.mock import AsyncMock

from handlers.general.start import get_home_menu


@pytest.mark.asyncio
async def test_get_home_menu_empty_cart(mock_persistence_layer):
    """Test get_home_menu with empty cart."""
    # Arrange
    user_id = 12345
    first_name = "Alice"
    mock_persistence_layer.get_cart_items.return_value = {}

    # Act
    text, keyboard = await get_home_menu(mock_persistence_layer, user_id, first_name)

    # Assert
    assert "Welcome" in text
    assert any("Shop Now" in button.text for row in keyboard.inline_keyboard for button in row)
    assert not any("Checkout" in button.text for row in keyboard.inline_keyboard for button in row)


@pytest.mark.asyncio
async def test_get_home_menu_active_cart(mock_persistence_layer):
    """Test get_home_menu with active cart."""
    # Arrange
    user_id = 12345
    first_name = "Alice"
    mock_persistence_layer.get_cart_items.return_value = {"product_1": 2}

    # Act
    text, keyboard = await get_home_menu(mock_persistence_layer, user_id, first_name)

    # Assert
    assert "Welcome" in text
    assert "You have items in your cart" in text
    assert any("Continue Shopping" in button.text for row in keyboard.inline_keyboard for button in row)
    assert any("Checkout" in button.text for row in keyboard.inline_keyboard for button in row)
    assert any(button.callback_data == "view_cart" for row in keyboard.inline_keyboard for button in row)
