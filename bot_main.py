import logging

from telegram.ext import ApplicationBuilder

import config
from handlers.owner.set_owner import set_owner_handler
from handlers.product.add_product import get_add_product_handler
from handlers.customer.cart import cart_handler
from handlers.customer.shop import (
    shop_start_handler,
    category_selection_handler,
    product_selection_handler,
    add_to_cart_handler,
    close_shop_handler,
    back_to_categories_handler,
    back_to_products_handler,
)
from persistence.in_memory_persistence import InMemoryPersistence


logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")
    persistence_instance = InMemoryPersistence()

    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    application.bot_data["persistence"] = persistence_instance

    application.add_handler(set_owner_handler)
    application.add_handler(get_add_product_handler())
    application.add_handler(shop_start_handler)
    application.add_handler(category_selection_handler)
    application.add_handler(product_selection_handler)
    application.add_handler(add_to_cart_handler)
    application.add_handler(close_shop_handler)
    application.add_handler(back_to_categories_handler)
    application.add_handler(back_to_products_handler)
    application.add_handler(cart_handler)
    logger.info("Bot application built and handlers added. Starting polling...")

    application.run_polling()
    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    main()
