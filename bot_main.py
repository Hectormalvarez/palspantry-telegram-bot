import logging
from telegram.ext import CommandHandler, ContextTypes, ApplicationBuilder
from telegram import Update

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


async def set_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Access the persistence instance from application_data
    # We'll ensure it's put there in the main() function
    persistence: AbstractPantryPersistence = context.application_data["persistence"]

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


def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")

    # Create an instance of our persistence layer
    persistence_instance = InMemoryPersistence()

    # Use ApplicationBuilder for more explicit setup
    # and store the persistence instance in application_data
    application = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .application_data(
            {"persistence": persistence_instance}
        )  # Store persistence here
        .build()
    )

    # Add command handler
    application.add_handler(CommandHandler("set_owner", set_owner))

    logger.info("Bot application built and handlers added. Starting polling...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    main()
