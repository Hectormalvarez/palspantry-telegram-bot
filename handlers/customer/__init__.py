from telegram.ext import Application

from .shop import (
    shop_start_handler,
    category_selection_handler,
    product_selection_handler,
    add_to_cart_handler,
    close_shop_handler,
    back_to_categories_handler,
    back_to_products_handler,
    shop_home_callback_handler,
)
from .cart import (
    cart_command_handler,
    view_cart_handler,
    clear_cart_handler,
    checkout_handler,
)

def register_handlers(application: Application):
    """Registers all customer-related handlers (Shop & Cart)."""
    # Shop Handlers
    application.add_handler(shop_start_handler)
    application.add_handler(shop_home_callback_handler)
    application.add_handler(category_selection_handler)
    application.add_handler(product_selection_handler)
    application.add_handler(add_to_cart_handler)
    application.add_handler(close_shop_handler)
    application.add_handler(back_to_categories_handler)
    application.add_handler(back_to_products_handler)
    
    # Cart Handlers
    application.add_handler(cart_command_handler)
    application.add_handler(view_cart_handler)
    application.add_handler(clear_cart_handler)
    application.add_handler(checkout_handler)