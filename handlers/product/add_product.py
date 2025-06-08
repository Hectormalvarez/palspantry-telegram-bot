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

from handlers.utils import owner_only_command

logger = logging.getLogger(__name__)

# --- Conversation States for Adding a Product (In Progress) ---
PRODUCT_NAME = 0  # State for receiving the product name
PRODUCT_DESCRIPTION = 1  # State for receiving the product description
PRODUCT_PRICE = 2  # State for receiving the product price
PRODUCT_QUANTITY = 3  # For receiving product quantity
PRODUCT_CATEGORY = 4  # Placeholder for the state after quantity
PRODUCT_CONFIRMATION = 5


# --- Start Add Product Conversation Handlers ---
async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the product addition conversation by asking for the product name."""
    if not await owner_only_command(update, context):
        return ConversationHandler.END

    # Initialize a dictionary in user_data to store product details temporarily
    context.user_data["new_product"] = {}

    await update.message.reply_text(
        "Let's add a new product! First, what is the product's name?"
    )
    logger.info(
        "Owner %s started /addproduct. Asking for product name.",
        update.effective_user.id,
    )
    return PRODUCT_NAME  # Transition to the PRODUCT_NAME state


async def received_product_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Stores the product name and asks for product description."""
    product_name = update.message.text

    if not product_name or len(product_name.strip()) == 0:
        await update.message.reply_text(
            "Product name cannot be empty. Please enter a name, "
            "or type /cancel to exit."
        )
        return PRODUCT_NAME  # Stay in the same state, ask for name again

    context.user_data["new_product"]["name"] = product_name.strip()
    logger.info(
        "Received product name: '%s' from owner %s.",
        product_name,
        update.effective_user.id,
    )

    await update.message.reply_text(
        f"Great! Product name is '{product_name}'.\n\n"
        "Now, please enter a description for the product."
    )
    return PRODUCT_DESCRIPTION  # <-- TRANSITION TO NEW STATE


async def received_product_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Stores product description and asks for the product price."""
    product_description = update.message.text

    if not product_description or len(product_description.strip()) == 0:
        await update.message.reply_text(
            "Product description cannot be empty. Please enter a description, "
            "or type /cancel to exit."
        )
        return PRODUCT_DESCRIPTION  # Stay in the same state, ask for description again

    context.user_data["new_product"]["description"] = product_description.strip()
    logger.info(
        "Received product description for '%s' from owner %s. Description: '%s...'",
        context.user_data["new_product"]["name"],
        update.effective_user.id,
        product_description[:30],
    )

    await update.message.reply_text(
        "Description noted.\n\n"
        "Now, what's the price for this product? Please enter a number "
        "(e.g., 10.99 or 5)."
    )

    return PRODUCT_PRICE  # <--(no longer ends conversation here)


async def received_product_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Stores product price after validation and asks for the product quantity.
    """
    price_text = update.message.text
    converted_price: float | None = None  # Initialize to None

    # Attempt to convert the input text to a float
    if price_text:  # Check if text is not None or empty before trying to convert
        try:
            converted_price = float(price_text)
        except ValueError:
            # If float(price_text) raises a ValueError (e.g., for "abc"),
            # converted_price will remain None.
            logger.debug(
                "Price input '%s' could not be converted to float.", price_text
            )

    # Now, validate the converted_price (it must be a number and positive)
    if converted_price is None or converted_price <= 0:
        logger.warning(
            "Invalid price input: '%s' (converted: %s) from owner %s.",
            price_text,
            converted_price,
            update.effective_user.id,
        )
        await update.message.reply_text(
            "That doesn't look like a valid price. "
            "Please enter a positive number (e.g., 10.99 or 5), or type /cancel."
        )
        return PRODUCT_PRICE  # Stay in the same state to re-collect price

    # If we reach here, the price is valid
    context.user_data["new_product"]["price"] = converted_price
    product_name = context.user_data["new_product"].get("name", "the product")
    logger.info(
        "Received product price: %s for '%s' from owner %s.",
        converted_price,
        product_name,
        update.effective_user.id,
    )

    await update.message.reply_text(
        f"Price set to {converted_price:.2f}.\n\n"
        "Now, how many units of this product are available? "
        "Please enter a whole number (e.g., 10)."
    )

    # Transition to the PRODUCT_QUANTITY state
    logger.debug("Product data so far: %s", context.user_data["new_product"])
    # Do NOT delete new_product here, as it's needed for the next step
    return PRODUCT_QUANTITY


async def received_product_quantity(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Stores product quantity (after validation) and transitions to asking for category.
    """
    quantity_text = update.message.text
    product_name = context.user_data.get("new_product", {}).get("name", "the product")

    # Try to convert and validate in one go
    try:
        # The .strip() is important if you want to treat
        # "   " as potentially invalid before int()
        # or allow int(" 5 ") to work. int() can handle leading/trailing whitespace.
        if (
            not quantity_text or not quantity_text.strip()
        ):  # Explicitly catch empty/whitespace first if desired for logging
            logger.warning(
                "Empty quantity input for '%s' from owner %s.",
                product_name,
                update.effective_user.id,
            )
            # Let it fall through to the ValueError or a specific check, or handle here
            # For a unified message, we let the int conversion or value check fail.

        quantity = int(quantity_text)  # Try to convert to int
        if quantity <= 0:
            # This will be caught by the generic ValueError message below
            # if we don't have a specific message for "positive"
            raise ValueError("Quantity must be a positive integer.")

        context.user_data["new_product"]["quantity"] = quantity
        logger.info(
            "Received product quantity: %s for '%s' from owner %s.",
            quantity,
            product_name,
            update.effective_user.id,
        )

        await update.message.reply_text(
            f"Quantity set to {quantity}.\n\n"
            "Next, please specify a category for this product."
        )
        return PRODUCT_CATEGORY

    except ValueError:  # Catches int() conversion errors and quantity <= 0
        logger.warning(
            "Invalid quantity input: '%s' for '%s' from owner %s.",
            quantity_text,
            product_name,
            update.effective_user.id,
        )
        await update.message.reply_text(
            "That doesn't look like a valid quantity. "
            "Please enter a whole positive number (e.g., 10), or type /cancel."
        )
        return PRODUCT_QUANTITY


async def received_product_category(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Stores product category (text input for now) and transitions to confirmation.
    """
    category_name_input = update.message.text
    user_product_data = context.user_data.get("new_product", {})  # More robust get
    product_name_for_log = user_product_data.get("name", "the product")

    if not category_name_input or not category_name_input.strip():
        logger.warning(
            "Empty category input for '%s' from owner %s.",
            product_name_for_log,
            update.effective_user.id,
        )
        await update.message.reply_text(
            "Category name cannot be empty. Please enter a category, or type /cancel."
        )
        return PRODUCT_CATEGORY  # Stay in the same state

    normalized_category = category_name_input.strip()
    user_product_data["category"] = normalized_category

    logger.info(
        "Received product category: '%s' for '%s' from owner %s.",
        normalized_category,
        product_name_for_log,
        update.effective_user.id,
    )

    # Prepare the confirmation message with all collected details
    # (Assuming name, description, price, quantity are already in user_product_data)
    summary_message = (
        "Okay, let's confirm the details for your new product:\n\n"
        f"Name: {user_product_data.get('name', 'N/A')}\n"
        f"Description: {user_product_data.get('description', 'N/A')}\n"
        f"Price: ${user_product_data.get('price', 0.0):.2f}\n"
        f"Quantity: {user_product_data.get('quantity', 0)}\n"
        f"Category: {normalized_category}\n\n"
        "Is everything correct?"
    )

    # Define Inline Keyboard buttons
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Confirm & Save", callback_data="product_confirm_save"
            ),
            InlineKeyboardButton("✏️ Edit", callback_data="product_confirm_edit"),
            InlineKeyboardButton("❌ Cancel", callback_data="product_confirm_cancel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(summary_message, reply_markup=reply_markup)

    logger.info(
        "Confirmation shown for product '%s'. Awaiting user choice.",
        product_name_for_log,
    )
    return PRODUCT_CONFIRMATION  # Transition to await button callback


# Placeholder functions for button callbacks (we'll implement these next)
async def handle_product_save_confirmed(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()  # Important to answer callback queries

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    product_data = context.user_data.get("new_product")
    product_name = product_data.get("name", "the product")

    if not product_data:
        logger.error(
            "User %s tried to save product but 'new_product' data was missing.",
            update.effective_user.id,
        )
        await query.edit_message_text(
            "An error occurred: Product data not found."
            "Please try adding the product again."
        )
        return ConversationHandler.END

    product_id = await persistence.add_product(product_data)

    if product_id:
        success_message = f"✅ Product '{product_name}' (ID: {product_id}) added!"
        logger.info(
            "Product '%s' (ID: %s) saved by owner %s.",
            product_name,
            product_id,
            update.effective_user.id,
        )
        await query.edit_message_text(text=success_message)
    else:
        failure_message = (
            f"❌ Failed to add product '{product_name}'. Please try again later."
        )
        logger.error(
            "Failed to save product '%s' for owner %s.",
            product_name,
            update.effective_user.id,
        )
        await query.edit_message_text(text=failure_message)

    # Clear the temporary product data
    if "new_product" in context.user_data:
        del context.user_data["new_product"]
        logger.debug("Cleared 'new_product' from user_data.")

    return ConversationHandler.END


async def handle_product_edit_choice(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="Product edit feature not implemented yet. Conversation ended."
    )
    logger.info("Placeholder: Product edit chosen.")
    if "new_product" in context.user_data:
        del context.user_data["new_product"]
    return ConversationHandler.END


async def handle_product_cancel_from_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # This can often be the same logic as your existing /cancel command's handler
    query = update.callback_query
    await query.answer()
    # Let's reuse the main cancel logic if it's suitable, or implement separately
    if "new_product" in context.user_data:
        logger.info(
            "Cancelling product addition from confirmation. Cleared data: %s",
            context.user_data["new_product"],
        )
        del context.user_data["new_product"]
    else:
        logger.info(
            "Product addition cancelled from confirmation before any data was stored."
        )

    # Edit the message to remove buttons and show cancelled state
    await query.edit_message_text(text="Product addition cancelled.")
    return ConversationHandler.END


async def cancel_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the product addition conversation."""
    if "new_product" in context.user_data:
        logger.info(
            "Cancelling product addition. Cleared data: %s",
            context.user_data["new_product"],
        )
        del context.user_data["new_product"]  # Clean up any partially collected data
    else:
        logger.info("Product addition cancelled before any data was stored.")

    await update.message.reply_text(
        "Product addition cancelled.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def get_add_product_handler() -> ConversationHandler:
    """Builds and returns the ConversationHandler for adding a product."""
    return ConversationHandler(
        entry_points=[CommandHandler("addproduct", add_product_start)],
        states={
            PRODUCT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_product_name),
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
            PRODUCT_CONFIRMATION: [
                CallbackQueryHandler(
                    handle_product_save_confirmed, pattern="^product_confirm_save$"
                ),
                CallbackQueryHandler(
                    handle_product_edit_choice, pattern="^product_confirm_edit$"
                ),
                CallbackQueryHandler(
                    handle_product_cancel_from_confirmation,
                    pattern="^product_confirm_cancel$",
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_add_product)],
        per_message=False,
    )
