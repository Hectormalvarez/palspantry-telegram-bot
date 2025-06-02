import logging

from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update


import config

logger = logging.getLogger(__name__)
BOT_OWNER = None


async def set_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global BOT_OWNER
    user_id = update.effective_user.id
    username = update.effective_user.username

    logger.info(f"User {user_id} (username: {username}) attempted to use /set_owner.")

    if BOT_OWNER is None:
        BOT_OWNER = user_id
        logger.info(f"Bot owner set to user_id: {user_id} (username: {username}).")
        await update.message.reply_text(f"You are now the owner of this bot.")
    else:
        await update.message.reply_text("An owner has already been set.")


def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")

    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler("set_owner", set_owner))

    logger.info("Bot application built and handlers added. Starting polling...")

    application.run_polling()
    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    main()
