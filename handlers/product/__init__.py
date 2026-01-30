from telegram.ext import Application
from .add_product import get_add_product_handler

def register_handlers(application: Application):
    """Registers all product-related handlers."""
    # Note: get_add_product_handler is a function that returns the ConversationHandler
    application.add_handler(get_add_product_handler())