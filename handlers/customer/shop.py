from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler

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


async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles a user clicking a category button.
    Displays the products in the selected category.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    # The category name is captured from the regex in the CallbackQueryHandler
    category_name = context.matches[0].group(1)

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    products = await persistence.get_products_by_category(category_name)

    if not products:
        await query.edit_message_text(
            text="There are currently no products available in this category."
        )
        return

    # Format the product list into a string
    product_list_text = [f"Products in {category_name}:"]
    for product in products:
        product_list_text.append(f"- {product['name']} (${product['price']:.2f})")

    await query.edit_message_text(text="\n".join(product_list_text))


shop_start_handler = CommandHandler("shop", shop_start)


category_selection_handler = CallbackQueryHandler(
    handle_category_selection, pattern="^category_(.+)"
)
