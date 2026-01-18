import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    first_name = update.effective_user.first_name
    logger.info(f"User {update.effective_user.id} started the bot.")

    keyboard = [[InlineKeyboardButton("🛍️ Shop Now", callback_data="shop_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"Welcome, {first_name}! \n\nI am the PalsPantry Bot. I can help you browse our inventory and place orders."

    await update.message.reply_text(text, reply_markup=reply_markup)
