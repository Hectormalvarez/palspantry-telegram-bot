import pytest
from unittest.mock import ANY

from telegram import Update, User, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from handlers.general.start import start_command


@pytest.mark.asyncio
async def test_start_command(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test /start command handler."""
    # Arrange
    mock_update_message.effective_user.first_name = "Alice"

    # Act
    await start_command(mock_update_message, mock_telegram_context)

    # Assert
    mock_update_message.message.reply_text.assert_called_once()
    call_args = mock_update_message.message.reply_text.call_args
    reply_text = call_args.args[0] if call_args.args else call_args.kwargs.get("text")
    assert "Welcome, Alice!" in reply_text

    # Check reply_markup
    sent_markup = call_args.kwargs.get("reply_markup")
    assert isinstance(sent_markup, InlineKeyboardMarkup)

    # Check for the shop button
    keyboard = sent_markup.inline_keyboard
    shop_button_found = False
    for row in keyboard:
        for button in row:
            if button.text == "🛍️ Shop Now" and button.callback_data == "shop_start":
                shop_button_found = True
                break
        if shop_button_found:
            break
    assert shop_button_found, "Shop Now button with callback_data 'shop_start' not found"
