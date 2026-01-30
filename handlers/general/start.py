import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from handlers.utils import schedule_deletion
from persistence.abstract_persistence import AbstractPantryPersistence
from resources.strings import Strings

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
        text = Strings.General.welcome_returning_user(first_name)
        keyboard = [
            [InlineKeyboardButton(Strings.General.CONTINUE_SHOPPING_BTN, callback_data="shop_start")],
            [InlineKeyboardButton(Strings.General.CHECKOUT_BTN, callback_data="view_cart")]
        ]
    else:
        text = Strings.General.welcome_new_user(first_name)
        keyboard = [[InlineKeyboardButton(Strings.General.SHOP_NOW_BTN, callback_data="shop_start")]]

    return text, InlineKeyboardMarkup(keyboard)
