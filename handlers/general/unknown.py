import logging

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown messages."""
    logger.info(f"Unknown message from user {update.effective_user.id}: {update.message.text}")

    text = "Sorry, I didn't understand that. Please use /start to begin or /shop to browse the menu."
    await update.message.reply_text(text)


unknown_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown)
