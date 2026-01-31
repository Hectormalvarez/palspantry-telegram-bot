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
from handlers.utils import owner_only_command, schedule_deletion, _delete_user_message
from resources.strings import Strings

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

    if update.message:
        schedule_deletion(
            context, update.effective_chat.id, update.message.message_id, delay=3.0
        )

    # FIX: Use effective_message to prevent NoneType errors on edge cases
    sent_message = await update.effective_message.reply_text(Strings.Product.START_ADD)
    context.user_data["last_bot_msg_id"] = sent_message.message_id
    return PRODUCT_NAME


async def received_product_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(
        context, update.effective_chat.id, update.message.message_id, delay=3.0
    )
    product_name = update.message.text
    if not product_name or not product_name.strip():
        await update.message.reply_text(Strings.Product.ERR_EMPTY_NAME)
        return PRODUCT_NAME

    context.user_data["new_product"]["name"] = product_name.strip()

    # NEW LINE: Delete old message
    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    # UPDATED LINE: Capture sent message
    sent_message = await update.message.reply_text(
        Strings.Product.ASK_DESCRIPTION.format(name=product_name)
    )

    # NEW LINE: Save new ID for next turn
    context.user_data["last_bot_msg_id"] = sent_message.message_id

    return PRODUCT_DESCRIPTION


async def received_product_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(
        context, update.effective_chat.id, update.message.message_id, delay=3.0
    )
    desc = update.message.text
    if not desc or not desc.strip():
        await update.message.reply_text(Strings.Product.ERR_EMPTY_DESC)
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
    schedule_deletion(
        context, update.effective_chat.id, update.message.message_id, delay=3.0
    )
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
            Strings.Product.ASK_QUANTITY.format(price=price)
        )

        context.user_data["last_bot_msg_id"] = sent_message.message_id

        return PRODUCT_QUANTITY
    except ValueError:
        await update.message.reply_text(Strings.Product.ERR_INVALID_PRICE)
        return PRODUCT_PRICE


async def received_product_quantity(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(
        context, update.effective_chat.id, update.message.message_id, delay=3.0
    )
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
            Strings.Product.ASK_CATEGORY.format(qty=qty)
        )

        context.user_data["last_bot_msg_id"] = sent_message.message_id

        return PRODUCT_CATEGORY
    except ValueError:
        await update.message.reply_text(Strings.Product.ERR_INVALID_QTY)
        return PRODUCT_QUANTITY


async def received_product_category(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    schedule_deletion(
        context, update.effective_chat.id, update.message.message_id, delay=3.0
    )
    cat = update.message.text
    if not cat or not cat.strip():
        await update.message.reply_text(Strings.Product.ERR_EMPTY_CATEGORY)
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
    schedule_deletion(
        context, update.effective_chat.id, update.message.message_id, delay=3.0
    )
    """Stores the file_id of the largest available photo size."""
    photo_file = update.message.photo[-1]  # Get the largest size
    context.user_data["new_product"]["image_file_id"] = photo_file.file_id

    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    await _send_confirmation(update, context)
    return PRODUCT_CONFIRMATION


async def skip_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    schedule_deletion(
        context, update.effective_chat.id, update.message.message_id, delay=3.0
    )
    """Sets image_file_id to None and proceeds."""
    context.user_data["new_product"]["image_file_id"] = None

    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    sent_message = await update.message.reply_text(Strings.Product.NO_IMAGE_ADDED)
    context.user_data["last_bot_msg_id"] = sent_message.message_id

    last_msg_id = context.user_data.get("last_bot_msg_id")
    if last_msg_id:
        schedule_deletion(context, update.effective_chat.id, last_msg_id, delay=3.0)

    await _send_confirmation(update, context)
    return PRODUCT_CONFIRMATION


async def _send_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Helper to display the confirmation summary."""
    p = context.user_data["new_product"]

    summary = Strings.Product.confirm_summary(
        name=p.get("name"),
        desc=p.get("description"),
        price=p.get("price"),
        qty=p.get("quantity"),
        cat=p.get("category"),
        has_image=bool(p.get("image_file_id")),
    )

    keyboard = [
        [
            InlineKeyboardButton(
                Strings.Product.BTN_CONFIRM, callback_data="product_confirm_save"
            ),
            InlineKeyboardButton(
                Strings.Product.BTN_CANCEL, callback_data="product_confirm_cancel"
            ),
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
        await query.edit_message_text(Strings.Product.ERR_DATA_LOST)
        return ConversationHandler.END

    product_id = await persistence.add_product(product_data)

    if product_id:
        await query.edit_message_text(
            Strings.Product.SUCCESS_ADDED.format(name=product_data["name"])
        )
        schedule_deletion(
            context, update.effective_chat.id, query.message.message_id, delay=5.0
        )
    else:
        await query.edit_message_text(Strings.Product.ERR_DB_SAVE)
        schedule_deletion(
            context, update.effective_chat.id, query.message.message_id, delay=5.0
        )

    context.user_data.pop("new_product", None)
    return ConversationHandler.END


async def cancel_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the conversation. Handles both /cancel command and 'Cancel' button."""
    context.user_data.pop("new_product", None)

    # Check if this came from a button click (CallbackQuery)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(Strings.Product.CANCELLED)
        schedule_deletion(
            context,
            update.effective_chat.id,
            update.callback_query.message.message_id,
            delay=5.0,
        )
    # Check if this came from a text command (/cancel)
    elif update.message:
        await _delete_user_message(update)
        sent = await update.message.reply_text(
            Strings.Product.CANCELLED, reply_markup=ReplyKeyboardRemove()
        )
        schedule_deletion(context, update.effective_chat.id, sent.message_id, delay=5.0)
    # Fallback for any other update type
    elif update.effective_message:
        await update.effective_message.reply_text(Strings.Product.CANCELLED)
        schedule_deletion(
            context,
            update.effective_chat.id,
            update.effective_message.message_id,
            delay=5.0,
        )

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
