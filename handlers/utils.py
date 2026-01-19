import logging
from telegram import Update
from telegram.ext import ContextTypes
from persistence.abstract_persistence import AbstractPantryPersistence

logger = logging.getLogger(__name__)


async def _delete_msg_job(context: ContextTypes.DEFAULT_TYPE):
    """Job callback to delete a message."""
    job = context.job
    try:
        chat_id, message_id = job.data
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        # It's common for messages to be missing if user deleted them manually
        logging.getLogger(__name__).debug(f"Cleanup failed: {e}")


def schedule_deletion(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: float = 3.0):
    """
    Schedules a message to be deleted after `delay` seconds.
    Safe to call even if job_queue is None (no-op).
    """
    if context.job_queue:
        context.job_queue.run_once(_delete_msg_job, delay, data=(chat_id, message_id))


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
