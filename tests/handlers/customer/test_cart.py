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
