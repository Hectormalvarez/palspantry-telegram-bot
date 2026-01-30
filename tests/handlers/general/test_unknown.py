import pytest
from unittest.mock import ANY
from resources.strings import Strings

from telegram import Update
from telegram.ext import ContextTypes

from handlers.general.unknown import handle_unknown


@pytest.mark.asyncio
async def test_unknown_command(
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test unknown command handler."""
    # Arrange
    mock_update_message.message.text = "Hello there"

    # Act
    await handle_unknown(mock_update_message, mock_telegram_context)

    # Assert
    mock_update_message.message.reply_text.assert_called_once()
    call_args = mock_update_message.message.reply_text.call_args
    reply_text = call_args.args[0] if call_args.args else call_args.kwargs.get("text")
    assert reply_text == Strings.Error.UNKNOWN_COMMAND
