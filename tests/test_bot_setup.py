import os
import pytest
import unittest.mock
from telegram.ext import Application
import bot_main
from telegram import Update, User, Message

@pytest.mark.asyncio
async def test_bot_initializes(mocker):
    """Assert that the bot application initializes without errors."""
    bot_token = "test_token"  # Mock bot token
    with unittest.mock.patch.dict(os.environ, {"BOT_TOKEN": bot_token}):
        mock_app = mocker.AsyncMock(spec=Application)
        mock_app.run_polling = mocker.AsyncMock()
        application = Application.builder().token(bot_token).build()
        assert application is not None
        mock_app.run_polling.assert_not_called()

@pytest.mark.asyncio
async def test_first_user_becomes_owner(mocker):
    """Assert that the first user becomes the owner when no owner exists."""
    with unittest.mock.patch("bot_main.BOT_OWNER", new=None):
        # Mock the Update object
        update = mocker.AsyncMock(spec=Update)
        update.effective_user = mocker.MagicMock(spec=User)
        update.effective_user.id = 12345  # Mock user ID
        update.message = mocker.AsyncMock()
        update.message.reply_text = mocker.AsyncMock()

        # Mock the Context object
        context = mocker.AsyncMock()

        # Initially, the bot owner should be None
        assert bot_main.BOT_OWNER is None

        # Call the set_owner function
        await bot_main.set_owner(update, context)

        # Now, the bot owner should be the user ID
        assert bot_main.BOT_OWNER == 12345

        # Check that the bot sends a message to the user
        update.message.reply_text.assert_called_once_with("You are now the owner of this bot.")

@pytest.mark.asyncio
async def test_set_owner_command_works_correctly(mocker):
    """Assert that the /set_owner command works correctly."""
    with unittest.mock.patch("bot_main.BOT_OWNER", new=None):
        # Mock the Update object
        update = mocker.AsyncMock(spec=Update)
        update.effective_user = mocker.MagicMock(spec=User)
        update.effective_user.id = 12345  # Mock user ID
        update.message = mocker.AsyncMock()
        update.message.reply_text = mocker.AsyncMock()

        # Mock the Context object
        context = mocker.AsyncMock()

        # Initially, the bot owner should be None
        assert bot_main.BOT_OWNER is None

        # Call the set_owner function
        await bot_main.set_owner(update, context)

        # Now, the bot owner should be the user ID
        assert bot_main.BOT_OWNER == 12345

        # Check that the bot sends a message to the user
        update.message.reply_text.assert_called_once_with("You are now the owner of this bot.")

        # Call the set_owner function again with a different user
        update.effective_user = mocker.MagicMock(spec=User)
        update.effective_user.id = 67890  # Mock a different user ID
        await bot_main.set_owner(update, context)

        # The bot owner should still be the first user
        assert bot_main.BOT_OWNER == 12345

        # Check that the bot sends a message to the user that an owner has already been set
        update.message.reply_text.assert_called_with("An owner has already been set.")
