from telegram.ext import Application
from .set_owner import set_owner_handler


def register_handlers(application: Application):
    """Registers all owner-related handlers."""
    application.add_handler(set_owner_handler)
