import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ApplicationBuilder,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Import configuration (this will also initialize logging)
import config

# Import persistence layer
from persistence.in_memory_persistence import InMemoryPersistence
from persistence.abstract_persistence import (
    AbstractPantryPersistence,
)  # For type hinting


# Get a logger for this module
logger = logging.getLogger(__name__)


# --- Conversation States for Adding a Product (In Progress) ---
PRODUCT_NAME = 0  # State for receiving the product name
PRODUCT_DESCRIPTION = 1  # State for receiving the product description
PRODUCT_PRICE = 2  # State for receiving the product price
# We'll add more states like PRODUCT_QUANTITY etc. later


async def set_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Access the persistence instance from bot_data
    # We'll ensure it's put there in the main() function
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]

    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"

    logger.info(f"User {user_id} (username: {username}) attempted to use /set_owner.")

    # Check if an owner is already set using the persistence layer
    if not await persistence.is_owner_set():
        # Try to set the owner using the persistence layer
        success = await persistence.set_bot_owner(user_id)
        if success:
            logger.info(
                f"Bot owner set to user_id: {user_id} (username: {username}) via persistence layer."
            )
            await update.message.reply_text(f"You are now the owner of this bot.")
        else:
            # This case might be rare if is_owner_set() was false, but good for completeness
            # or if set_bot_owner had other internal reasons to fail.
            current_owner = await persistence.get_bot_owner()  # Re-fetch to be sure
            logger.warning(
                f"User {user_id} (username: {username}) tried to set owner, "
                f"but persistence.set_bot_owner returned false. Current owner: {current_owner}."
            )
            await update.message.reply_text(
                "Could not set owner at this time. An owner might already be registered."
            )
    else:
        current_owner_id = await persistence.get_bot_owner()
        logger.warning(
            f"User {user_id} (username: {username}) tried to set owner, "
            f"but owner is already {current_owner_id} (checked via persistence layer)."
        )
        await update.message.reply_text("An owner has already been set.")


# --- Helper for Owner-Only Commands ---
async def owner_only_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    """Helper to check if the user is the bot owner."""
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    owner_id = await persistence.get_bot_owner()
    if not owner_id or update.effective_user.id != owner_id:
        if update.message:  # Check if update.message exists
            await update.message.reply_text(
                "Sorry, this command is only for the bot owner."
            )
        logger.warning(
            f"User {update.effective_user.id} (not owner) tried an owner command."
        )
        return False
    return True


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
        f"Owner {update.effective_user.id} started /addproduct. Asking for product name."
    )
    return PRODUCT_NAME  # Transition to the PRODUCT_NAME state


async def received_product_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Stores the product name and ends the conversation (for now)."""
    product_name = update.message.text

    if not product_name or len(product_name.strip()) == 0:
        await update.message.reply_text(
            "Product name cannot be empty. Please enter a name, or type /cancel to exit."
        )
        return PRODUCT_NAME  # Stay in the same state, ask for name again

    context.user_data["new_product"]["name"] = product_name.strip()
    logger.info(
        f"Received product name: '{product_name}' from owner {update.effective_user.id}."
    )

    await update.message.reply_text(
        f"Great! Product name is '{product_name}'.\n\n"
        "Now, please enter a description for the product."  # <-- Ask for description
    )
    return PRODUCT_DESCRIPTION  # <-- TRANSITION TO NEW STATE


async def received_product_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Stores product description and (for now) ends the conversation, preparing for price."""
    product_description = update.message.text

    if not product_description or len(product_description.strip()) == 0:
        await update.message.reply_text(
            "Product description cannot be empty. Please enter a description, or type /cancel to exit."
        )
        return PRODUCT_DESCRIPTION  # Stay in the same state, ask for description again

    context.user_data["new_product"]["description"] = product_description.strip()
    logger.info(
        f"Received product description for '{context.user_data['new_product']['name']}' "
        f"from owner {update.effective_user.id}. Description: '{product_description[:30]}...'"
    )

    await update.message.reply_text(
        f"Description noted.\n\n"
        "Now, what's the price for this product? Please enter a number (e.g., 10.99 or 5)."  # Ask for price
    )

    return PRODUCT_PRICE  # <--(no longer ends conversation here)


async def received_product_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Stores product price (after validation) and, for this incremental step,
    ends the conversation with a placeholder for the next step (quantity).
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
            logger.debug(f"Price input '{price_text}' could not be converted to float.")
            pass  # We'll handle the None case in the if block below

    # Now, validate the converted_price (it must be a number and positive)
    if converted_price is None or converted_price <= 0:
        logger.warning(
            f"Invalid price input: '{price_text}' (converted: {converted_price}) "
            f"from owner {update.effective_user.id}."
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
        f"Received product price: {converted_price} for '{product_name}' "
        f"from owner {update.effective_user.id}."
    )

    await update.message.reply_text(
        f"Price set to {converted_price:.2f}.\n\n"  # Format to 2 decimal places
        "Next, we'll ask for the quantity. (Quantity step not implemented yet)."  # Placeholder
    )

    # For this incremental step, we end the conversation here.
    # Later, this will return PRODUCT_QUANTITY.
    if "new_product" in context.user_data:
        logger.debug(f"Product data so far: {context.user_data['new_product']}")
        del context.user_data["new_product"]  # Clean up temporary data
    return ConversationHandler.END


async def cancel_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the product addition conversation."""
    if "new_product" in context.user_data:
        logger.info(
            f"Cancelling product addition. Cleared data: {context.user_data['new_product']}"
        )
        del context.user_data["new_product"]  # Clean up any partially collected data
    else:
        logger.info("Product addition cancelled before any data was stored.")

    await update.message.reply_text(
        "Product addition cancelled.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")

    # Create an instance of our persistence layer
    persistence_instance = InMemoryPersistence()

    # Use ApplicationBuilder for more explicit setup
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    application.bot_data["persistence"] = persistence_instance

    # Conversation handler for adding products
    add_product_conv_handler = ConversationHandler(
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
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_add_product)],
    )

    # Add command handler
    application.add_handler(CommandHandler("set_owner", set_owner))
    application.add_handler(add_product_conv_handler)

    logger.info("Bot application built and handlers added. Starting polling...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    main()
