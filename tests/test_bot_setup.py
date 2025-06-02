import pytest
from unittest import mock  # unittest.mock can be used alongside pytest-mock (mocker)
from telegram import Bot, Update, User
from telegram.ext import Application

# Import the module that contains BOT_OWNER and set_owner,
# and also the module we need to patch for BOT_TOKEN
import bot_main
import config  # Important for patching


@pytest.mark.asyncio
async def test_bot_initializes_application_object(mocker):
    """Assert that the Telegram Application object can be initialized with a token."""
    test_token = "fake_test_token_for_init_test"

    mocker.patch("config.BOT_TOKEN", test_token)

    application = Application.builder().token(test_token).build()
    assert application is not None
    assert application.bot is not None  # Check if the Bot object was created
    assert isinstance(application.bot, Bot)  # Ensure it's the correct type
    assert application.bot.token == test_token  # Check the token on the Bot object


@pytest.mark.asyncio
async def test_first_user_becomes_owner(mocker):
    """Assert that the first user becomes the owner when no owner exists."""
    # Reset BOT_OWNER in bot_main for this test case
    with mock.patch("bot_main.BOT_OWNER", new=None):
        # Mock the Update object
        update = mocker.AsyncMock(spec=Update)
        update.effective_user = mocker.MagicMock(spec=User)
        update.effective_user.id = 12345  # Mock user ID
        update.message = mocker.AsyncMock()
        update.message.reply_text = mocker.AsyncMock()

        # Mock the Context object (though not explicitly used by set_owner, good practice)
        context = mocker.AsyncMock()

        # Initially, the bot owner should be None
        assert bot_main.BOT_OWNER is None

        # Call the set_owner function
        await bot_main.set_owner(update, context)

        # Now, the bot owner should be the user ID
        assert bot_main.BOT_OWNER == 12345

        # Check that the bot sends a message to the user
        update.message.reply_text.assert_called_once_with(
            "You are now the owner of this bot."
        )


@pytest.mark.asyncio
async def test_set_owner_command_handles_owner_already_set(
    mocker,
):  # Renamed for clarity
    """Assert that /set_owner tells a user an owner is set if one exists."""
    # Set an initial owner ID for this test case
    initial_owner_id = 12345
    with mock.patch("bot_main.BOT_OWNER", new=initial_owner_id):
        # Mock the Update object for a new user trying to set owner
        update = mocker.AsyncMock(spec=Update)
        update.effective_user = mocker.MagicMock(spec=User)
        update.effective_user.id = 67890  # A different user ID
        update.message = mocker.AsyncMock()
        update.message.reply_text = mocker.AsyncMock()

        # Mock the Context object
        context = mocker.AsyncMock()

        # The bot owner is already set
        assert bot_main.BOT_OWNER == initial_owner_id

        # Call the set_owner function by the new user
        await bot_main.set_owner(update, context)

        # The bot owner should still be the initial user
        assert bot_main.BOT_OWNER == initial_owner_id

        # Check that the bot sends the correct message
        update.message.reply_text.assert_called_once_with(
            "An owner has already been set."
        )


@pytest.mark.asyncio
async def test_set_owner_command_allows_first_user_and_rejects_second(mocker):
    """Asserts the full /set_owner logic: first user accepted, second rejected."""
    # Ensure BOT_OWNER is None at the start of this test
    with mock.patch("bot_main.BOT_OWNER", new=None) as mock_bot_owner_global:
        # --- First User ---
        update_user1 = mocker.AsyncMock(spec=Update)
        update_user1.effective_user = mocker.MagicMock(spec=User)
        update_user1.effective_user.id = 11111  # User 1 ID
        update_user1.message = mocker.AsyncMock()
        update_user1.message.reply_text = mocker.AsyncMock()
        context1 = mocker.AsyncMock()

        await bot_main.set_owner(update_user1, context1)
        assert bot_main.BOT_OWNER == 11111  # Check global directly after call
        update_user1.message.reply_text.assert_called_once_with(
            "You are now the owner of this bot."
        )

        # --- Second User ---
        update_user2 = mocker.AsyncMock(spec=Update)
        update_user2.effective_user = mocker.MagicMock(spec=User)
        update_user2.effective_user.id = 22222  # User 2 ID
        update_user2.message = mocker.AsyncMock()
        update_user2.message.reply_text = (
            mocker.AsyncMock()
        )  # Fresh mock for reply_text
        context2 = mocker.AsyncMock()

        await bot_main.set_owner(update_user2, context2)
        assert bot_main.BOT_OWNER == 11111  # Owner should NOT have changed
        update_user2.message.reply_text.assert_called_once_with(
            "An owner has already been set."
        )
