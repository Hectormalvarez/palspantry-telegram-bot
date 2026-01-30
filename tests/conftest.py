import os
import tempfile
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from telegram import Update, User
from telegram.ext import ContextTypes

from persistence.abstract_persistence import AbstractPantryPersistence
from persistence.sqlite_persistence import SQLitePersistence

# --- Integration Test Fixtures ---


@pytest_asyncio.fixture
async def sqlite_persistence_layer():
    """
    Creates a temporary SQLite database for integration testing.
    Yields a live SQLitePersistence instance connected to the temp file.
    Teardown removes the temp file.
    """
    # 1. Create a temp file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close the file descriptor, we only need the path

    # 2. Initialize Persistence (this runs the schema creation script)
    persistence = SQLitePersistence(db_path=path)

    # 3. Yield to the test
    yield persistence

    # 4. Teardown: Delete the file
    if os.path.exists(path):
        os.remove(path)


# --- Unit Test Mocks (for Handlers) ---


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
    context.bot = mocker.AsyncMock()
    return context


@pytest.fixture
def mock_update_message(mocker) -> AsyncMock:
    """
    Provides a basic mock Update object with a mock message and reply_text method.
    The effective_user needs to be set by the test.
    """
    update = mocker.AsyncMock(spec=Update)
    update.message = mocker.AsyncMock()
    update.message.reply_text = mocker.AsyncMock()

    # NEW: Add effective_message for handlers that use it
    update.effective_message = mocker.AsyncMock()
    update.effective_message.reply_text = mocker.AsyncMock()

    # NEW: Add effective_chat for handlers that use send_message
    update.effective_chat = mocker.AsyncMock()
    update.effective_chat.send_message = mocker.AsyncMock()

    return update


@pytest.fixture
def mock_update_callback_query(mocker) -> AsyncMock:
    """
    Provides a mock Update object representing a callback query from an inline button.
    """
    update = mocker.AsyncMock(spec=Update)
    update.callback_query = mocker.AsyncMock()
    update.callback_query.answer = mocker.AsyncMock()
    update.callback_query.edit_message_text = mocker.AsyncMock()
    update.callback_query.message = mocker.AsyncMock()
    update.callback_query.message.photo = None

    # NEW: Ensure delete() is awaitable
    update.callback_query.message.delete = mocker.AsyncMock()

    # NEW: Add effective_chat for handlers that use send_message
    update.effective_chat = mocker.AsyncMock()
    update.effective_chat.send_message = mocker.AsyncMock()

    update.effective_user = mocker.MagicMock(spec=User, id=98765)
    return update
