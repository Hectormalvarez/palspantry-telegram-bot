import os
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

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
    # Get the bot token from the environment variable
    bot_token = os.environ.get("BOT_TOKEN")

    # Create the application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # Add command handler
    application.add_handler(CommandHandler("set_owner", set_owner))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
