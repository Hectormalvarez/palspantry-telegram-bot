import logging

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from resources.strings import Strings

logger = logging.getLogger(__name__)


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown messages."""
    logger.info(f"Unknown message from user {update.effective_user.id}: {update.message.text}")

    await update.message.reply_text(Strings.Error.UNKNOWN_COMMAND)


unknown_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown)
