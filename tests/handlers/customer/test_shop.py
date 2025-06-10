import pytest
from unittest.mock import ANY

from telegram import Update, User, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from handlers.customer import shop
from persistence.abstract_persistence import AbstractPantryPersistence


@pytest.mark.asyncio
async def test_shop_start_with_categories(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /shop command when categories exist."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=98765)
    mock_categories = ["Bakery", "Drinks"]
    mock_persistence_layer.get_all_categories.return_value = mock_categories

    # Act
    await shop.shop_start(mock_update_message, mock_telegram_context)

    # Assert
    mock_persistence_layer.get_all_categories.assert_called_once()
    mock_update_message.message.reply_text.assert_called_once_with(
        "Welcome to the shop! Please select a category to browse:",
        reply_markup=ANY,
    )
    # Check that the call included a keyboard
    sent_markup = mock_update_message.message.reply_text.call_args.kwargs.get(
        "reply_markup"
    )
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 2  # 2 rows
    assert sent_markup.inline_keyboard[0][0].text == "Bakery"
    assert sent_markup.inline_keyboard[1][0].text == "Drinks"


@pytest.mark.asyncio
async def test_shop_start_no_categories(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /shop command when the shop is empty."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=98765)
    mock_persistence_layer.get_all_categories.return_value = []

    # Act
    await shop.shop_start(mock_update_message, mock_telegram_context)

    # Assert
    mock_persistence_layer.get_all_categories.assert_called_once()
    mock_update_message.message.reply_text.assert_called_once_with(
        "The shop is currently empty. Please check back later!"
    )


@pytest.mark.asyncio
async def test_handle_category_selection_with_products(
    mocker,
    mock_update_callback_query: Update,  # Uses our new fixture
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test category button click when products are found."""
    # Arrange
    category_name = "Bakery"
    mock_update_callback_query.callback_query.data = f"category_{category_name}"

    # Mock the context.matches to simulate regex capture
    mock_match = mocker.MagicMock()
    mock_match.group.return_value = category_name
    mock_telegram_context.matches = [mock_match]

    mock_products = [
        {"name": "Croissant", "price": 2.50},
        {"name": "Baguette", "price": 3.00},
    ]
    mock_persistence_layer.get_products_by_category.return_value = mock_products

    # Act
    await shop.handle_category_selection(
        mock_update_callback_query, mock_telegram_context
    )

    # Assert
    mock_update_callback_query.callback_query.answer.assert_called_once()
    mock_persistence_layer.get_products_by_category.assert_called_once_with(
        category_name
    )

    expected_text = "Products in Bakery:\n- Croissant ($2.50)\n- Baguette ($3.00)"
    mock_update_callback_query.callback_query.edit_message_text.assert_called_once_with(
        text=expected_text
    )


@pytest.mark.asyncio
async def test_handle_category_selection_no_products(
    mocker,
    mock_update_callback_query: Update,  # Uses our new fixture
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test category button click when category is empty."""
    # Arrange
    category_name = "Empty Category"
    mock_update_callback_query.callback_query.data = f"category_{category_name}"

    mock_match = mocker.MagicMock()
    mock_match.group.return_value = category_name
    mock_telegram_context.matches = [mock_match]

    mock_persistence_layer.get_products_by_category.return_value = []

    # Act
    await shop.handle_category_selection(
        mock_update_callback_query, mock_telegram_context
    )

    # Assert
    mock_update_callback_query.callback_query.answer.assert_called_once()
    mock_persistence_layer.get_products_by_category.assert_called_once_with(
        category_name
    )

    expected_text = "There are currently no products available in this category."
    mock_update_callback_query.callback_query.edit_message_text.assert_called_once_with(
        text=expected_text
    )
