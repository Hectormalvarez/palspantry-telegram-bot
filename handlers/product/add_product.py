"""
This module contains all the handlers and business logic for the
/addproduct conversation flow.
"""

import logging
from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from persistence.abstract_persistence import AbstractPantryPersistence
from handlers.utils import owner_only_command, schedule_deletion

logger = logging.getLogger(__name__)

# --- Conversation States ---
PRODUCT_NAME = 0
PRODUCT_DESCRIPTION = 1
PRODUCT_PRICE = 2
PRODUCT_QUANTITY = 3
PRODUCT_CATEGORY = 4
PRODUCT_IMAGE = 5
PRODUCT_CONFIRMATION = 6


# --- Start Add Product Conversation Handlers ---
async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the product addition conversation by asking for the product name."""
    if not await owner_only_command(update, context):
        return ConversationHandler.END

    context.user_data["new_product"] = {}

    # FIX: Use effective_message to prevent NoneType errors on edge cases
    sent_message = await update.effective_message.reply_text(
        "Let's add a new product! First, what is the product's name?"
    )
    context.user_data["last_bot_msg_id"] = sent_message.message_id
    return PRODUCT_NAME


async def received_product_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(context, update.effective_chat.id, update.message.message_id, delay=3.0)
    product_name = update.message.text
    if not product_name or not product_name.strip():
        await update.message.reply_text(
            "Product name cannot be empty. Please enter a name, or /cancel."
        )
        return PRODUCT_NAME

    context.user_data["new_product"]["name"] = product_name.strip()

    # NEW LINE: Delete old message
    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    # UPDATED LINE: Capture sent message
    sent_message = await update.message.reply_text(
        f"Name set to '{product_name}'.\n\nNow, please enter a description."
    )

    # NEW LINE: Save new ID for next turn
    context.user_data["last_bot_msg_id"] = sent_message.message_id

    return PRODUCT_DESCRIPTION


async def received_product_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(context, update.effective_chat.id, update.message.message_id, delay=3.0)
    desc = update.message.text
    if not desc or not desc.strip():
        await update.message.reply_text(
            "Description cannot be empty. Please enter a description, or /cancel."
        )
        return PRODUCT_DESCRIPTION

    context.user_data["new_product"]["description"] = desc.strip()

    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    sent_message = await update.message.reply_text(
        "Description noted.\n\nNow, what's the price? (e.g., 10.99 or 5)"
    )

    context.user_data["last_bot_msg_id"] = sent_message.message_id

    return PRODUCT_PRICE


async def received_product_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(context, update.effective_chat.id, update.message.message_id, delay=3.0)
    price_text = update.message.text
    try:
        price = float(price_text)
        if price <= 0:
            raise ValueError
        context.user_data["new_product"]["price"] = price

        last_msg_id = context.user_data.get("last_bot_msg_id")
        if last_msg_id:
            schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

        sent_message = await update.message.reply_text(
            f"Price set to ${price:.2f}.\n\nHow many units are available? (e.g., 10)"
        )

        context.user_data["last_bot_msg_id"] = sent_message.message_id

        return PRODUCT_QUANTITY
    except ValueError:
        await update.message.reply_text(
            "Invalid price. Please enter a positive number (e.g. 10.99), or /cancel."
        )
        return PRODUCT_PRICE


async def received_product_quantity(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(context, update.effective_chat.id, update.message.message_id, delay=3.0)
    qty_text = update.message.text
    try:
        qty = int(qty_text)
        if qty < 0:
            raise ValueError
        context.user_data["new_product"]["quantity"] = qty

        last_msg_id = context.user_data.get("last_bot_msg_id")
        if last_msg_id:
            schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

        sent_message = await update.message.reply_text(
            f"Quantity set to {qty}.\n\nNow, please specify a category (e.g. 'Dairy')."
        )

        context.user_data["last_bot_msg_id"] = sent_message.message_id

        return PRODUCT_CATEGORY
    except ValueError:
        await update.message.reply_text(
            "Invalid quantity. Please enter a whole positive number, or /cancel."
        )
        return PRODUCT_QUANTITY


async def received_product_category(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(context, update.effective_chat.id, update.message.message_id, delay=3.0)
    cat = update.message.text
    if not cat or not cat.strip():
        await update.message.reply_text(
            "Category cannot be empty. Please enter a category, or /cancel."
        )
        return PRODUCT_CATEGORY

    context.user_data["new_product"]["category"] = cat.strip()

    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    sent_message = await update.message.reply_text(
        "Category set.\n\n"
        "Finally, please send a photo of the product.\n"
        "Or type /skip if you don't want to add an image."
    )

    context.user_data["last_bot_msg_id"] = sent_message.message_id

    return PRODUCT_IMAGE


async def received_product_image(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(context, update.effective_chat.id, update.message.message_id, delay=3.0)
    """Stores the file_id of the largest available photo size."""
    photo_file = update.message.photo[-1]  # Get the largest size
    context.user_data["new_product"]["image_file_id"] = photo_file.file_id

    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    await _send_confirmation(update, context)
    return PRODUCT_CONFIRMATION


async def skip_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    schedule_deletion(context, update.effective_chat.id, update.message.message_id, delay=3.0)
    """Sets image_file_id to None and proceeds."""
    context.user_data["new_product"]["image_file_id"] = None

    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    sent_message = await update.message.reply_text("No image added.")
    context.user_data["last_bot_msg_id"] = sent_message.message_id

    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    await _send_confirmation(update, context)
    return PRODUCT_CONFIRMATION


async def _send_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Helper to display the confirmation summary."""
    p = context.user_data["new_product"]

    summary = (
        "<b>Confirm New Product:</b>\n\n"
        f"<b>Name:</b> {p.get('name')}\n"
        f"<b>Desc:</b> {p.get('description')}\n"
        f"<b>Price:</b> ${p.get('price'):.2f}\n"
        f"<b>Qty:</b> {p.get('quantity')}\n"
        f"<b>Cat:</b> {p.get('category')}\n"
        f"<b>Image:</b> {'Yes' if p.get('image_file_id') else 'No'}\n\n"
        "Save this product?"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Confirm & Save", callback_data="product_confirm_save"
            ),
            InlineKeyboardButton("❌ Cancel", callback_data="product_confirm_cancel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        summary, reply_markup=reply_markup, parse_mode="HTML"
    )


async def handle_product_save_confirmed(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    product_data = context.user_data.get("new_product")

    if not product_data:
        await query.edit_message_text("Error: Data lost. Please try again.")
        return ConversationHandler.END

    product_id = await persistence.add_product(product_data)

    if product_id:
        await query.edit_message_text(f"✅ Product '{product_data['name']}' added!")
    else:
        await query.edit_message_text("❌ Database error. Could not save.")

    context.user_data.pop("new_product", None)
    return ConversationHandler.END


async def cancel_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the conversation. Handles both /cancel command and 'Cancel' button."""
    context.user_data.pop("new_product", None)

    # Check if this came from a button click (CallbackQuery)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Product addition cancelled.")
    # Check if this came from a text command (/cancel)
    elif update.message:
        await update.message.reply_text(
            "Product addition cancelled.", reply_markup=ReplyKeyboardRemove()
        )
    # Fallback for any other update type
    elif update.effective_message:
        await update.effective_message.reply_text("Product addition cancelled.")

    return ConversationHandler.END


def get_add_product_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("addproduct", add_product_start)],
        states={
            PRODUCT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_product_name)
            ],
            PRODUCT_DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, received_product_description
                )
            ],
            PRODUCT_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_product_price)
            ],
            PRODUCT_QUANTITY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, received_product_quantity
                )
            ],
            PRODUCT_CATEGORY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, received_product_category
                )
            ],
            PRODUCT_IMAGE: [
                MessageHandler(filters.PHOTO, received_product_image),
                CommandHandler("skip", skip_product_image),
            ],
            PRODUCT_CONFIRMATION: [
                CallbackQueryHandler(
                    handle_product_save_confirmed, pattern="^product_confirm_save$"
                ),
                CallbackQueryHandler(
                    cancel_add_product, pattern="^product_confirm_cancel$"
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_add_product)],
    )
