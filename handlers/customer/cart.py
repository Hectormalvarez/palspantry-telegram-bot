from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler

from persistence.abstract_persistence import AbstractPantryPersistence


async def handle_cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /cart command for the customer."""
    cart_items = context.user_data.get("cart", {})

    if not cart_items:
        # Keyboard for the empty cart scenario
        keyboard = [[
            InlineKeyboardButton(
                "🛍️ Continue Shopping", callback_data="navigate_to_categories"
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Your cart is empty. Use /shop to browse our products!",
            reply_markup=reply_markup,
        )
        return

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    
    cart_lines = []
    total_price = 0.0

    for product_id, quantity in cart_items.items():
        product = await persistence.get_product(product_id)
        if product:
            subtotal = quantity * product["price"]
            total_price += subtotal
            cart_lines.append(
                f"- {product['name']} ({quantity} x ${product['price']:.2f}) = ${subtotal:.2f}"
            )
        else:
            cart_lines.append(
                f"- [Product ID: {product_id} not found] (Quantity: {quantity})"
            )

    cart_text = "\n".join(cart_lines)
    
    final_text = (
        "Here is your cart:\n\n"
        f"{cart_text}\n\n"
        f"Total: ${total_price:.2f}"
    )

    # Create the keyboard for a non-empty cart
    keyboard = [
        [InlineKeyboardButton("✅ Place Order", callback_data="place_order")],
        [
            InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart"),
            InlineKeyboardButton(
                "🛍️ Continue Shopping", callback_data="navigate_to_categories"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(final_text, reply_markup=reply_markup)


# Create the handler instance for the /cart command
cart_handler = CommandHandler("cart", handle_cart_command)
