# FILE: tests/test_bot_setup.py
import pytest
from unittest.mock import AsyncMock  # For type hinting fixture arguments
from telegram import Update, User, Bot
from telegram.ext import ApplicationBuilder

import bot_main
from persistence.abstract_persistence import AbstractPantryPersistence


@pytest.mark.asyncio
async def test_bot_initializes_application_object(mocker):
    """Assert that the Telegram Application object can be initialized with a token."""
    test_token = "fake_test_token_for_init_test"
    mocker.patch("config.BOT_TOKEN", test_token)

    application = ApplicationBuilder().token(test_token).build()

    assert application is not None
    assert application.bot is not None
    assert isinstance(application.bot, Bot)
    assert application.bot.token == test_token


@pytest.mark.asyncio
async def test_first_user_becomes_owner(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: AsyncMock,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Assert that the first user becomes the owner when no owner exists."""
    mock_persistence_layer.is_owner_set.return_value = False
    mock_persistence_layer.set_bot_owner.return_value = True

    user_id_to_set = 12345
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=user_id_to_set)

    await bot_main.set_owner(mock_update_message, mock_telegram_context)

    mock_persistence_layer.is_owner_set.assert_called_once()
    mock_persistence_layer.set_bot_owner.assert_called_once_with(user_id_to_set)
    mock_update_message.message.reply_text.assert_called_once_with(
        "You are now the owner of this bot."
    )


@pytest.mark.asyncio
async def test_set_owner_command_handles_owner_already_set(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: AsyncMock,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Assert that /set_owner tells a user an owner is set if one exists."""
    initial_owner_id = 12345
    mock_persistence_layer.is_owner_set.return_value = True
    mock_persistence_layer.get_bot_owner.return_value = initial_owner_id

    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=67890)

    await bot_main.set_owner(mock_update_message, mock_telegram_context)

    mock_persistence_layer.is_owner_set.assert_called_once()
    mock_persistence_layer.get_bot_owner.assert_called_once()
    mock_persistence_layer.set_bot_owner.assert_not_called()
    mock_update_message.message.reply_text.assert_called_once_with(
        "An owner has already been set."
    )


@pytest.mark.asyncio
async def test_set_owner_command_allows_first_user_and_rejects_second(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: AsyncMock,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Asserts the full /set_owner logic: first user accepted, second rejected."""
    user1_id = 11111
    user2_id = 22222

    # --- First User Attempt ---
    mock_persistence_layer.is_owner_set.return_value = False
    mock_persistence_layer.set_bot_owner.return_value = True

    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=user1_id)
    mock_update_message.message.reply_text.reset_mock()

    await bot_main.set_owner(mock_update_message, mock_telegram_context)

    mock_persistence_layer.is_owner_set.assert_called_once()
    mock_persistence_layer.set_bot_owner.assert_called_once_with(user1_id)
    mock_update_message.message.reply_text.assert_called_once_with(
        "You are now the owner of this bot."
    )

    # --- Second User Attempt ---
    mock_persistence_layer.is_owner_set.return_value = True
    mock_persistence_layer.get_bot_owner.return_value = user1_id
    mock_persistence_layer.is_owner_set.reset_mock()  # Reset for this specific call check
    mock_persistence_layer.get_bot_owner.reset_mock()  # Reset for this specific call check
    # set_bot_owner's call_count is cumulative and should remain 1

    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=user2_id)
    mock_update_message.message.reply_text.reset_mock()

    await bot_main.set_owner(mock_update_message, mock_telegram_context)

    mock_persistence_layer.is_owner_set.assert_called_once()
    mock_persistence_layer.get_bot_owner.assert_called_once()
    assert (
        mock_persistence_layer.set_bot_owner.call_count == 1
    )  # Still only called once in total
    mock_update_message.message.reply_text.assert_called_once_with(
        "An owner has already been set."
    )
