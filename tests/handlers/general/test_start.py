import pytest
from unittest.mock import ANY
from resources.strings import Strings

from telegram import Update, User, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from handlers.general.start import start_command


@pytest.mark.asyncio
async def test_start_command(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer,
):
    """Test /start command handler."""
    # Arrange
    mock_update_message.effective_user.first_name = "Alice"
    mock_telegram_context.job_queue = mocker.Mock()
    mock_persistence_layer.get_cart_items.return_value = {}

    # Act
    await start_command(mock_update_message, mock_telegram_context)

    # Assert
    mock_update_message.message.reply_text.assert_called_once()
    call_args = mock_update_message.message.reply_text.call_args
    reply_text = call_args.args[0] if call_args.args else call_args.kwargs.get("text")
    assert reply_text == Strings.General.welcome_new_user("Alice")

    # Check reply_markup
    sent_markup = call_args.kwargs.get("reply_markup")
    assert isinstance(sent_markup, InlineKeyboardMarkup)

    # Check for the shop button
    keyboard = sent_markup.inline_keyboard
    shop_button_found = False
    for row in keyboard:
        for button in row:
            if (
                button.text == Strings.General.SHOP_NOW_BTN
                and button.callback_data == "shop_start"
            ):
                shop_button_found = True
                break
        if shop_button_found:
            break
    assert (
        shop_button_found
    ), "Shop Now button with callback_data 'shop_start' not found"

    assert mock_telegram_context.job_queue.run_once.call_count >= 1


@pytest.mark.asyncio
async def test_get_home_menu_empty_cart(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer,
):
    """Test get_home_menu with empty cart."""
    # Arrange
    from handlers.general.start import get_home_menu

    mock_persistence_layer.get_cart_items.return_value = {}
    user_id = 123
    first_name = "Alice"

    # Act
    text, reply_markup = await get_home_menu(
        mock_persistence_layer, user_id, first_name
    )

    # Assert
    assert text == Strings.General.welcome_new_user("Alice")

    # Check reply_markup
    assert isinstance(reply_markup, InlineKeyboardMarkup)
    keyboard = reply_markup.inline_keyboard
    shop_button_found = False
    for row in keyboard:
        for button in row:
            if (
                button.text == Strings.General.SHOP_NOW_BTN
                and button.callback_data == "shop_start"
            ):
                shop_button_found = True
                break
        if shop_button_found:
            break
    assert (
        shop_button_found
    ), "Shop Now button with callback_data 'shop_start' not found"


@pytest.mark.asyncio
async def test_get_home_menu_active_cart(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer,
):
    """Test get_home_menu with active cart."""
    # Arrange
    from handlers.general.start import get_home_menu

    mock_persistence_layer.get_cart_items.return_value = {"item1": 2}
    user_id = 123
    first_name = "Alice"

    # Act
    text, reply_markup = await get_home_menu(
        mock_persistence_layer, user_id, first_name
    )

    # Assert
    assert text == Strings.General.welcome_returning_user("Alice")

    # Check reply_markup
    assert isinstance(reply_markup, InlineKeyboardMarkup)
    keyboard = reply_markup.inline_keyboard

    # Should have Continue Shopping and Checkout buttons
    continue_shopping_found = False
    checkout_found = False

    for row in keyboard:
        for button in row:
            if (
                button.text == Strings.General.CONTINUE_SHOPPING_BTN
                and button.callback_data == "shop_start"
            ):
                continue_shopping_found = True
            if (
                button.text == Strings.General.CHECKOUT_BTN
                and button.callback_data == "view_cart"
            ):
                checkout_found = True

    assert continue_shopping_found, "Continue Shopping button not found"
    assert checkout_found, "Checkout button not found"
