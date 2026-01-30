import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from handlers.utils import schedule_deletion
from persistence.abstract_persistence import AbstractPantryPersistence
from resources.strings import Strings

logger = logging.getLogger(__name__)


async def handle_cart_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles the /cart command to display the user's cart."""
    user_id = update.effective_user.id
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]

    cart_items = await persistence.get_cart_items(user_id=user_id)

    if not cart_items:
        # Empty cart
        text = Strings.Cart.EMPTY
        keyboard = [
            [
                InlineKeyboardButton(
                    Strings.General.CONTINUE_SHOPPING_BTN,
                    callback_data="navigate_to_categories",
                )
            ]
        ]
    else:
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
                message_lines.append(
                    Strings.Cart.item_line(name, quantity, price, item_total)
                )
            else:
                # Product not found, perhaps skip or handle
                pass

        message_lines.append(Strings.Cart.total_line(total))
        text = "\n".join(message_lines)

        keyboard = [
            [
                InlineKeyboardButton(
                    Strings.General.CHECKOUT_BTN, callback_data="cart_checkout"
                ),
                InlineKeyboardButton(
                    Strings.Cart.CLEAR_BTN, callback_data="clear_cart"
                ),
                InlineKeyboardButton(
                    Strings.General.CONTINUE_SHOPPING_BTN,
                    callback_data="navigate_to_categories",
                ),
            ]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text, reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)
        schedule_deletion(context, update.effective_chat.id, update.message.message_id)


async def handle_clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles clearing the user's cart."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    await persistence.clear_cart(user_id=user_id)

    await query.edit_message_text(text=Strings.Cart.CLEARED)


async def handle_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the checkout process."""
    query = update.callback_query
    user_id = update.effective_user.id
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]

    order_id = await persistence.create_order(user_id=user_id)
    if order_id is None:
        await query.answer(text=Strings.Cart.CHECKOUT_ERROR_EMPTY, show_alert=True)
        return

    order = await persistence.get_order(order_id=order_id)
    items = order["items"]
    total = order["total_amount"]

    # Format receipt
    receipt_lines = [Strings.Cart.RECEIPT_HEADER]
    for item in items:
        name = item["name"]
        qty = item["quantity"]
        price = item["unit_price"]
        receipt_lines.append(Strings.Cart.receipt_item(name, qty, price))
    receipt_lines.append(Strings.Cart.receipt_total(total))
    receipt_lines.append(Strings.Cart.RECEIPT_FOOTER)
    receipt = "\n".join(receipt_lines)

    await query.edit_message_text(text=receipt, parse_mode=ParseMode.HTML)

    # Notify owner
    owner_id = await persistence.get_bot_owner()
    if owner_id:
        item_lines = ["Items:"]
        for item in items:
            item_lines.append(f"- {item['name']} x {item['quantity']}")
        items_summary = "\n".join(item_lines)
        notification = Strings.Order.notification_new(
            user_id, order_id, items_summary, total
        )
        await context.bot.send_message(chat_id=owner_id, text=notification)


# Handler registration
cart_command_handler = CommandHandler("cart", handle_cart_command)
view_cart_handler = CallbackQueryHandler(handle_cart_command, pattern="^view_cart$")
clear_cart_handler = CallbackQueryHandler(handle_clear_cart, pattern="^clear_cart$")
checkout_handler = CallbackQueryHandler(handle_checkout, pattern="^cart_checkout$")
