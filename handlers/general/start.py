import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from handlers.utils import schedule_deletion
from persistence.abstract_persistence import AbstractPantryPersistence

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    first_name = update.effective_user.first_name
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot.")

    persistence = context.bot_data["persistence"]
    text, reply_markup = await get_home_menu(persistence, user_id, first_name)

    await update.message.reply_text(text, reply_markup=reply_markup)

    if update.message:
        schedule_deletion(context, update.effective_chat.id, update.message.message_id, delay=3.0)


async def get_home_menu(persistence: AbstractPantryPersistence, user_id: int, first_name: str):
    """Get the home menu for the user based on their cart status."""
    cart_items = await persistence.get_cart_items(user_id)

    if cart_items:
        text = f"Welcome back, {first_name}!\n\nYou have items in your cart."
        keyboard = [
            [InlineKeyboardButton("🛍️ Continue Shopping", callback_data="shop_start")],
            [InlineKeyboardButton("🛒 Checkout", callback_data="cart_checkout")]
        ]
    else:
        text = f"Welcome, {first_name}! \n\nI am the PalsPantry Bot. I can help you browse our inventory and place orders."
        keyboard = [[InlineKeyboardButton("🛍️ Shop Now", callback_data="shop_start")]]

    return text, InlineKeyboardMarkup(keyboard)
