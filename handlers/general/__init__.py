from telegram.ext import Application, CommandHandler

from .start import start_command
from .help import help_command
from .unknown import unknown_handler

def register_handlers(application: Application):
    """Registers all general command handlers."""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(unknown_handler)