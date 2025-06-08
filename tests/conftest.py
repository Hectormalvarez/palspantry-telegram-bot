from unittest.mock import AsyncMock  # Needed for the AsyncMock type hint

import pytest
from telegram import Update
from telegram.ext import ContextTypes

# Import your persistence abstraction for type hinting
from persistence.abstract_persistence import AbstractPantryPersistence


@pytest.fixture
def mock_persistence_layer(
    mocker,
) -> AsyncMock:  # type hint uses unittest.mock.AsyncMock
    """
    Provides a mock instance of AbstractPantryPersistence.
    Individual tests can configure its methods' return_values as needed.
    """
    return mocker.AsyncMock(spec=AbstractPantryPersistence)


@pytest.fixture
def mock_telegram_context(
    mocker, mock_persistence_layer: AbstractPantryPersistence
) -> AsyncMock:  # type hint uses unittest.mock.AsyncMock
    """
    Provides a mock Telegram ContextTypes.DEFAULT_TYPE object
    with the mock_persistence_layer already injected into application_data.
    """
    context = mocker.AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot_data = {"persistence": mock_persistence_layer}
    return context


@pytest.fixture
def mock_update_message(mocker) -> AsyncMock:  # type hint uses unittest.mock.AsyncMock
    """
    Provides a basic mock Update object with a mock message and reply_text method.
    The effective_user needs to be set by the test.
    """
    update = mocker.AsyncMock(spec=Update)  # spec uses telegram.Update
    update.message = mocker.AsyncMock()
    update.message.reply_text = mocker.AsyncMock()
    return update
