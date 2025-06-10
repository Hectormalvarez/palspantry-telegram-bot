from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes
from persistence.abstract_persistence import AbstractPantryPersistence

async def shop_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /shop command. Displays a list of product categories to the user.
    """
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    categories = await persistence.get_all_categories()

    if not categories:
        await update.message.reply_text(
            "The shop is currently empty. Please check back later!"
        )
        return

    keyboard = []
    for category in categories:
        # Each button is on its own row
        keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to the shop! Please select a category to browse:",
        reply_markup=reply_markup,
    )

shop_start_handler = CommandHandler("shop", shop_start)
