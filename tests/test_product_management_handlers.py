import pytest
from unittest.mock import AsyncMock
from telegram import Update, User
from telegram.ext import ContextTypes, ConversationHandler

import handlers.owner_handlers as owner_handlers
import handlers.product_management_handlers as product_management_handlers
from persistence.abstract_persistence import AbstractPantryPersistence


# --- Tests for my_products ---
@pytest.mark.asyncio
async def test_my_products_no_products_as_owner(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /myproducts when no products are added and user is the owner."""
    test_owner_id = 12345
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=test_owner_id)
    mock_persistence_layer.get_bot_owner.return_value = test_owner_id
    mock_persistence_layer.get_all_products.return_value = []

    await product_management_handlers.my_products(mock_update_message, mock_telegram_context)

    mock_persistence_layer.get_all_products.assert_called_once()
    mock_update_message.message.reply_text.assert_called_once_with(
        "You have not added any products yet."
    )


@pytest.mark.asyncio
async def test_my_products_with_products_as_owner(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /myproducts when products exist and user is the owner."""
    test_owner_id = 12345
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=test_owner_id)
    mock_persistence_layer.get_bot_owner.return_value = test_owner_id
    
    mock_products = [
        {"name": "Product A", "description": "Desc A", "price": 10.0, "quantity": 5},
        {"name": "Product B", "description": "Desc B", "price": 20.0, "quantity": 10},
    ]
    mock_persistence_layer.get_all_products.return_value = mock_products

    await product_management_handlers.my_products(mock_update_message, mock_telegram_context)

    expected_reply = (
        "Your Products:\n\n"
        "Name: Product A\nDescription: Desc A\nPrice: 10.00\nQuantity: 5\n\n"
        "Name: Product B\nDescription: Desc B\nPrice: 20.00\nQuantity: 10"
    )
    mock_persistence_layer.get_all_products.assert_called_once()
    mock_update_message.message.reply_text.assert_called_once_with(expected_reply)


@pytest.mark.asyncio
async def test_my_products_non_owner_access(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /myproducts when user is not the owner."""
    actual_owner_id = 12345
    non_owner_id = 67890
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=non_owner_id)
    mock_persistence_layer.get_bot_owner.return_value = actual_owner_id

    await product_management_handlers.my_products(mock_update_message, mock_telegram_context)

    mock_persistence_layer.get_all_products.assert_not_called()
    mock_update_message.message.reply_text.assert_called_once_with(
        "Sorry, this command is only for the bot owner."
    )
