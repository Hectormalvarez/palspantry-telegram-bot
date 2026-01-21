import pytest
from unittest.mock import ANY

from telegram import Update, User, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from handlers.customer import cart
from persistence.abstract_persistence import AbstractPantryPersistence


@pytest.mark.asyncio
async def test_handle_cart_command_empty(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /cart command when cart is empty."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=98765)
    mock_update_message.callback_query = None  # Ensure it's treated as a command
    mock_persistence_layer.get_cart_items.return_value = {}

    # Act
    await cart.handle_cart_command(mock_update_message, mock_telegram_context)

    # Assert
    mock_persistence_layer.get_cart_items.assert_called_once_with(user_id=98765)
    call_args = mock_update_message.message.reply_text.call_args
    assert call_args.kwargs["text"] == "Your cart is empty."
    sent_markup = call_args.kwargs["reply_markup"]
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 1
    assert sent_markup.inline_keyboard[0][0].text == "Continue Shopping"
    assert sent_markup.inline_keyboard[0][0].callback_data == "navigate_to_categories"


@pytest.mark.asyncio
async def test_handle_cart_command_with_items(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /cart command when cart has items."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=98765)
    mock_update_message.callback_query = None  # Ensure it's treated as a command
    mock_persistence_layer.get_cart_items.return_value = {"prod_1": 2}
    mock_persistence_layer.get_product.return_value = {"name": "Bread", "price": 3.00}

    # Act
    await cart.handle_cart_command(mock_update_message, mock_telegram_context)

    # Assert
    mock_persistence_layer.get_cart_items.assert_called_once_with(user_id=98765)
    mock_persistence_layer.get_product.assert_called_once_with("prod_1")
    call_args = mock_update_message.message.reply_text.call_args
    message_text = call_args.kwargs["text"]
    assert "- Bread (2 x $3.00) = $6.00" in message_text
    assert "Total: $6.00" in message_text
    sent_markup = call_args.kwargs["reply_markup"]
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 1
    buttons_row = sent_markup.inline_keyboard[0]
    button_texts = [btn.text for btn in buttons_row]
    assert "Checkout" in button_texts
    assert "Clear Cart" in button_texts
    assert "Continue Shopping" in button_texts
    # Find the Continue Shopping button and assert its callback_data
    continue_button = next(btn for btn in buttons_row if btn.text == "Continue Shopping")
    assert continue_button.callback_data == "navigate_to_categories"


@pytest.mark.asyncio
async def test_handle_clear_cart_callback(
    mocker,
    mock_update_callback_query: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test handle_clear_cart callback query."""
    # Arrange
    mock_update_callback_query.callback_query.data = "clear_cart"
    mock_persistence_layer.clear_cart.return_value = True

    # Act
    await cart.handle_clear_cart(mock_update_callback_query, mock_telegram_context)

    # Assert
    mock_persistence_layer.clear_cart.assert_called_once_with(user_id=98765)
    mock_update_callback_query.callback_query.edit_message_text.assert_called_once_with(
        text="Cart cleared."
    )
    mock_update_callback_query.callback_query.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_checkout_success(
    mocker,
    mock_update_callback_query: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test handle_checkout success."""
    # Arrange
    mock_update_callback_query.callback_query.data = "cart_checkout"
    mock_persistence_layer.create_order.return_value = "order-123"
    mock_persistence_layer.get_order.return_value = {
        "id": "order-123",
        "total_amount": 15.50,
        "items": [
            {"name": "Burger", "quantity": 1, "unit_price": 10.00},
            {"name": "Fries", "quantity": 1, "unit_price": 5.50}
        ]
    }
    mock_persistence_layer.get_bot_owner.return_value = 12345

    # Act
    await cart.handle_checkout(mock_update_callback_query, mock_telegram_context)

    # Assert
    mock_persistence_layer.create_order.assert_called_once_with(user_id=98765)
    mock_persistence_layer.get_order.assert_called_once_with(order_id="order-123")
    mock_persistence_layer.get_bot_owner.assert_called_once()
    call_args = mock_update_callback_query.callback_query.edit_message_text.call_args
    message_text = call_args.kwargs["text"]
    assert "Total: $15.50" in message_text
    assert "Burger" in message_text
    mock_telegram_context.bot.send_message.assert_called_once_with(
        chat_id=12345, text=mocker.ANY
    )
    notification_text = mock_telegram_context.bot.send_message.call_args.kwargs["text"]
    assert "New Order Received" in notification_text
    assert "Burger" in notification_text
    assert "Fries" in notification_text
    assert "x 1" in notification_text


@pytest.mark.asyncio
async def test_handle_cart_cleanup(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /cart command with cleanup scheduling."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=98765)
    mock_update_message.callback_query = None  # Ensure it's treated as a command
    mock_update_message.message.message_id = 123
    mock_telegram_context.job_queue = mocker.Mock()
    mock_persistence_layer.get_cart_items.return_value = {"item_1": 1}
    mock_persistence_layer.get_product.return_value = {"name": "Bread", "price": 3.00}

    # Act
    await cart.handle_cart_command(mock_update_message, mock_telegram_context)

    # Assert
    mock_telegram_context.job_queue.run_once.assert_called_once()


@pytest.mark.asyncio
async def test_handle_cart_via_callback(
    mocker,
    mock_update_callback_query: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test handle_cart_command via callback query."""
    # Arrange
    mock_update_callback_query.callback_query.data = "view_cart"
    mock_persistence_layer.get_cart_items.return_value = {"item_1": 1}
    mock_persistence_layer.get_product.return_value = {"name": "Bread", "price": 3.00}

    # Act
    await cart.handle_cart_command(mock_update_callback_query, mock_telegram_context)

    # Assert
    mock_update_callback_query.callback_query.answer.assert_called_once()
    mock_update_callback_query.callback_query.edit_message_text.assert_called_once()
