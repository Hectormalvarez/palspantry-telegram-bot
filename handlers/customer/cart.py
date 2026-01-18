import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

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
        keyboard = [[InlineKeyboardButton("Continue Shopping", callback_data="navigate_to_categories")]]
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
            InlineKeyboardButton("Clear Cart", callback_data="clear_cart"),
            InlineKeyboardButton("Continue Shopping", callback_data="navigate_to_categories"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)


async def handle_clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles clearing the user's cart."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    await persistence.clear_cart(user_id=user_id)

    await query.edit_message_text(text="Cart cleared.")


async def handle_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the checkout process."""
    query = update.callback_query
    user_id = update.effective_user.id
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]

    order_id = await persistence.create_order(user_id=user_id)
    if order_id is not None:
        await query.edit_message_text(text=f"Order placed! Order ID: {order_id}")
    else:
        await query.answer(text="Cannot place order. Is your cart empty?", show_alert=True)


# Handler registration
cart_command_handler = CommandHandler("cart", handle_cart_command)
clear_cart_handler = CallbackQueryHandler(handle_clear_cart, pattern="^clear_cart$")
checkout_handler = CallbackQueryHandler(handle_checkout, pattern="^cart_checkout$")
