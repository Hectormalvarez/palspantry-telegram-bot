import pytest
from resources.strings import Strings

from handlers.general.help import help_command


@pytest.mark.asyncio
async def test_help_command(
    mock_update_message,
    mock_telegram_context,
):
    """Test /help command handler."""
    # Act
    await help_command(mock_update_message, mock_telegram_context)

    # Assert
    mock_update_message.message.reply_text.assert_called_once()
    call_args = mock_update_message.message.reply_text.call_args
    reply_text = call_args.args[0] if call_args.args else call_args.kwargs.get("text")
    assert reply_text == Strings.Help.MESSAGE
