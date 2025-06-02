from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update


import config

# Global variable to store the bot owner's user ID
BOT_OWNER = None


async def set_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global BOT_OWNER
    user_id = update.effective_user.id
    if BOT_OWNER is None:
        BOT_OWNER = user_id
        await update.message.reply_text(f"You are now the owner of this bot.")
    else:
        await update.message.reply_text("An owner has already been set.")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("set_owner", set_owner))
    application.run_polling()


if __name__ == "__main__":
    main()
