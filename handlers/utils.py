import logging
from telegram import Update
from telegram.ext import ContextTypes
from persistence.abstract_persistence import AbstractPantryPersistence

logger = logging.getLogger(__name__)


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
