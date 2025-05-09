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
        new_update = mocker.AsyncMock(spec=Update)
        new_update.effective_user = mocker.MagicMock(spec=User)
        new_update.effective_user.id = 67890  # Mock a different user ID
        new_update.message = mocker.AsyncMock()
        new_update.message.reply_text = mocker.AsyncMock()
        await bot_main.set_owner(new_update, context)

        # The bot owner should still be the first user
        assert bot_main.BOT_OWNER == 12345

        # Check that the bot sends a message to the user that an owner has already been set
        new_update.message.reply_text.assert_called_once_with("An owner has already been set.")

@pytest.mark.asyncio
async def test_add_product_command(mocker):
    """Assert that the /add_product command works correctly."""
    # Mock the Update object
    update = mocker.AsyncMock(spec=Update)
    update.effective_user = mocker.MagicMock(spec=User)
    update.message = mocker.AsyncMock()
    update.message.reply_text = mocker.AsyncMock()

    # Mock the Context object
    context = mocker.AsyncMock()
    context.args = ["Test Product", "10.0", "Test Category"]

    # Test case 1: Unauthorized access
    with unittest.mock.patch("bot_main.BOT_OWNER", new=67890):  # Mock a non-owner user ID
        update.effective_user.id = 12345  # Mock a non-owner user ID
        await bot_main.add_product(update, context)
        update.message.reply_text.assert_called_once_with("You are not authorized to use this command.")
        update.message.reply_text.reset_mock()

    # Test case 2: Successful product addition
    with unittest.mock.patch("bot_main.BOT_OWNER", new=12345):  # Mock the bot owner user ID
        update.effective_user.id = 12345  # Mock the bot owner user ID
        with unittest.mock.patch("database.add_product", return_value=True) as mock_add_product:
            await bot_main.add_product(update, context)
            mock_add_product.assert_called_once_with("Test Product", 10.0, "Test Category")
            update.message.reply_text.assert_called_once_with("Product 'Test Product' added successfully.")
            update.message.reply_text.reset_mock()

    # Test case 3: Product already exists
    with unittest.mock.patch("bot_main.BOT_OWNER", new=12345):  # Mock the bot owner user ID
        update.effective_user.id = 12345  # Mock the bot owner user ID
        with unittest.mock.patch("database.add_product", return_value=False) as mock_add_product:
            await bot_main.add_product(update, context)
            mock_add_product.assert_called_once_with("Test Product", 10.0, "Test Category")
            update.message.reply_text.assert_called_once_with("Failed to add product 'Test Product'. Product with this name may already exist.")
            update.message.reply_text.reset_mock()

    # Test case 4: Invalid input (missing arguments)
    with unittest.mock.patch("bot_main.BOT_OWNER", new=12345):  # Mock the bot owner user ID
        update.effective_user.id = 12345  # Mock the bot owner user ID
        context.args = ["Test Product", "10.0"]  # Missing category
        await bot_main.add_product(update, context)
        update.message.reply_text.assert_called_once_with("Usage: /add_product <name> <price> <category>")
        update.message.reply_text.reset_mock()

    # Test case 5: Invalid input (invalid price)
    with unittest.mock.patch("bot_main.BOT_OWNER", new=12345):  # Mock the bot owner user ID
        update.effective_user.id = 12345  # Mock the bot owner user ID
        context.args = ["Test Product", "invalid_price", "Test Category"]
        await bot_main.add_product(update, context)
        update.message.reply_text.assert_called_once_with("Invalid price. Price must be a number.")
        update.message.reply_text.reset_mock()
