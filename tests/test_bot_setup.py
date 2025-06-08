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
