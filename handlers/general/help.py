from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from resources.strings import Strings


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on available commands."""
    await update.message.reply_text(Strings.Help.MESSAGE, parse_mode=ParseMode.HTML)
