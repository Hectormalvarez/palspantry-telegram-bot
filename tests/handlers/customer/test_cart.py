import pytest
from unittest.mock import ANY
import pytest
from telegram import Update, User, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from handlers.customer.cart import handle_cart_command
from persistence.abstract_persistence import AbstractPantryPersistence


@pytest.mark.asyncio
async def test_cart_command_empty_sends_message(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test the /cart command when the user's cart is empty."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=12345)
    mock_telegram_context.user_data = {}

    # Act
    await handle_cart_command(mock_update_message, mock_telegram_context)

    # Assert
    mock_update_message.message.reply_text.assert_called_once_with(
        "Your cart is empty. Use /shop to browse our products!",
        reply_markup=ANY,
    )

    sent_markup = mock_update_message.message.reply_text.call_args.kwargs.get(
        "reply_markup"
    )
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 1
    button = sent_markup.inline_keyboard[0][0]
    assert button.text == "🛍️ Continue Shopping"
    assert button.callback_data == "navigate_to_categories"


@pytest.mark.asyncio
async def test_cart_command_with_one_item(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test the /cart command shows a single item's details."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=12345)

    # 1. Simulate a cart with ONE item.
    mock_telegram_context.user_data = {"cart": {"prod_123": 1}}

    # 2. Mock the persistence layer to return that one product.
    mock_product = {"id": "prod_123", "name": "Bread", "price": 2.50}
    mock_persistence_layer.get_product.return_value = mock_product

    # Act
    await handle_cart_command(mock_update_message, mock_telegram_context)

    # Assert
    # 3. Just check for a simple text output. No totals, no buttons.
    expected_text = "Here is your cart:\n\n- Bread (1 x $2.50) = $2.50\n\nTotal: $2.50"
    # MODIFIED ASSERTION: Check for reply_markup=ANY
    mock_update_message.message.reply_text.assert_called_once_with(
        expected_text,
        reply_markup=ANY,
    )

    # NEW ASSERTION: Verify the keyboard has the correct action buttons
    sent_markup = mock_update_message.message.reply_text.call_args.kwargs.get(
        "reply_markup"
    )
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 2  # Two rows of buttons

    # Check first row
    place_order_button = sent_markup.inline_keyboard[0][0]
    assert place_order_button.text == "✅ Place Order"
    assert place_order_button.callback_data == "place_order"

    # Check second row
    clear_cart_button = sent_markup.inline_keyboard[1][0]
    continue_shopping_button = sent_markup.inline_keyboard[1][1]
    assert clear_cart_button.text == "🗑️ Clear Cart"
    assert clear_cart_button.callback_data == "clear_cart"
    assert continue_shopping_button.text == "🛍️ Continue Shopping"
    assert continue_shopping_button.callback_data == "navigate_to_categories"


@pytest.mark.asyncio
async def test_cart_command_with_multiple_items_and_total(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test the /cart command with multiple items and a total price."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=12345)
    mock_telegram_context.user_data = {
        "cart": {"prod_123": 2, "prod_456": 1}
    }

    # Mock the persistence layer to return details for each product
    mock_product_1 = {"id": "prod_123", "name": "Bread", "price": 2.50}
    mock_product_2 = {"id": "prod_456", "name": "Milk", "price": 1.75}
    
    # Use side_effect to handle multiple calls to get_product
    async def get_product_side_effect(product_id):
        if product_id == "prod_123":
            return mock_product_1
        if product_id == "prod_456":
            return mock_product_2
        return None
        
    mock_persistence_layer.get_product.side_effect = get_product_side_effect

    # Act
    await handle_cart_command(mock_update_message, mock_telegram_context)

    # Assert
    expected_total = (2 * 2.50) + (1 * 1.75)  # 6.75
    expected_text = (
        "Here is your cart:\n\n"
        "- Bread (2 x $2.50) = $5.00\n"
        "- Milk (1 x $1.75) = $1.75\n\n"
        f"Total: ${expected_total:.2f}"
    )

    # MODIFIED ASSERTION: Check for reply_markup=ANY
    mock_update_message.message.reply_text.assert_called_once_with(
        expected_text,
        reply_markup=ANY,
    )

    # NEW ASSERTION: Verify the keyboard has the correct action buttons
    sent_markup = mock_update_message.message.reply_text.call_args.kwargs.get(
        "reply_markup"
    )
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 2  # Two rows of buttons

    # Check first row
    place_order_button = sent_markup.inline_keyboard[0][0]
    assert place_order_button.text == "✅ Place Order"
    assert place_order_button.callback_data == "place_order"

    # Check second row
    clear_cart_button = sent_markup.inline_keyboard[1][0]
    continue_shopping_button = sent_markup.inline_keyboard[1][1]
    assert clear_cart_button.text == "🗑️ Clear Cart"
    assert clear_cart_button.callback_data == "clear_cart"
    assert continue_shopping_button.text == "🛍️ Continue Shopping"
    assert continue_shopping_button.callback_data == "navigate_to_categories"
