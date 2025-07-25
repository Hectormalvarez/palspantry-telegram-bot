import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from persistence.abstract_persistence import AbstractPantryPersistence

logger = logging.getLogger(__name__)


async def set_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Access the persistence instance from bot_data
    # We'll ensure it's put there in the main() function
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]

    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"

    logger.info(
        "User %s (username: %s) attempted to use /set_owner.", user_id, username
    )

    # Check if an owner is already set using the persistence layer
    if not await persistence.is_owner_set():
        # Try to set the owner using the persistence layer
        success = await persistence.set_bot_owner(user_id)
        if success:
            logger.info(
                "Bot owner set to user_id: %s (username: %s) via persistence layer.",
                user_id,
                username,
            )
            await update.message.reply_text("You are now the owner of this bot.")
        else:
            # This case might be rare if is_owner_set() was false
            # or if set_bot_owner had other internal reasons to fail.
            current_owner = await persistence.get_bot_owner()  # Re-fetch to be sure
            logger.warning(
                "User %s (username: %s) tried to set owner, "
                "but persistence.set_bot_owner returned false. Current owner: %s.",
                user_id,
                username,
                current_owner,
            )
            await update.message.reply_text(
                "Could not set owner at this time. "
                "An owner might already be registered."
            )
    else:
        current_owner_id = await persistence.get_bot_owner()
        logger.warning(
            "User %s (username: %s) tried to set owner, "
            "but owner is already %s (checked via persistence layer).",
            user_id,
            username,
            current_owner_id,
        )
        await update.message.reply_text("An owner has already been set.")


set_owner_handler = CommandHandler("set_owner", set_owner)
