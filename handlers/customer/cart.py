import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes

from persistence.abstract_persistence import AbstractPantryPersistence


logger = logging.getLogger(__name__)


async def handle_cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /cart command to display the user's cart."""
    user_id = update.effective_user.id
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]

    cart_items = await persistence.get_cart_items(user_id=user_id)

    if not cart_items:
        # Empty cart
        text = "Your cart is empty."
        keyboard = [[InlineKeyboardButton("Continue Shopping", callback_data="cart_continue_shopping")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text=text, reply_markup=reply_markup)
        return

    # Cart has items
    total = 0.0
    message_lines = []
    for product_id, quantity in cart_items.items():
        product = await persistence.get_product(product_id)
        if product:
            name = product["name"]
            price = product["price"]
            item_total = quantity * price
            total += item_total
            message_lines.append(f"- {name} ({quantity} x ${price:.2f}) = ${item_total:.2f}")
        else:
            # Product not found, perhaps skip or handle
            pass

    message_lines.append(f"Total: ${total:.2f}")
    text = "\n".join(message_lines)

    keyboard = [
        [
            InlineKeyboardButton("Checkout", callback_data="cart_checkout"),
            InlineKeyboardButton("Clear Cart", callback_data="cart_clear"),
            InlineKeyboardButton("Continue Shopping", callback_data="cart_continue_shopping"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)


# Handler registration
cart_command_handler = CommandHandler("cart", handle_cart_command)
