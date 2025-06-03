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
)  # For type hinting if needed


# Get a logger for this module
logger = logging.getLogger(__name__)

# REMOVE the global BOT_OWNER variable
# BOT_OWNER = None # No longer needed here


# --- Conversation States for Adding a Product (Minimal for now) ---
PRODUCT_NAME = 0  # State for receiving the product name
# We'll add more states like PRODUCT_DESCRIPTION, PRODUCT_PRICE etc. later


async def set_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Access the persistence instance from bot_data
    # We'll ensure it's put there in the main() function
    persistence: AbstractPantryPersistence = context.bot_data['persistence']
    
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
    persistence: AbstractPantryPersistence = context.bot_data['persistence']
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
        f"Product name '{product_name}' received. "
        "More steps to add description, price, etc., will be implemented next!"
    )
    # For this first simple step, we end the conversation here.
    # Later, this will return the next state (e.g., PRODUCT_DESCRIPTION).
    # Clean up temporary data if ending here.
    if "new_product" in context.user_data:
        del context.user_data["new_product"]
    return ConversationHandler.END


async def cancel_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the product addition conversation."""
    if 'new_product' in context.user_data:
        logger.info(f"Cancelling product addition. Cleared data: {context.user_data['new_product']}")
        del context.user_data['new_product'] # Clean up any partially collected data
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
    application = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .build()
    )
    
    application.bot_data['persistence'] = persistence_instance
    
    # Conversation handler for adding products (minimal first step)
    add_product_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addproduct", add_product_start)],
        states={
            PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_product_name)],
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
