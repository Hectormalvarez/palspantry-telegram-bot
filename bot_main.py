import logging

from telegram.ext import ApplicationBuilder, CommandHandler

import config
from handlers import general, customer
from handlers.owner.set_owner import set_owner_handler
from handlers.product.add_product import get_add_product_handler
from persistence.sqlite_persistence import SQLitePersistence


logger = logging.getLogger(__name__)


def main() -> None:
    """
    Start the bot.

    Initializes the SQLite persistence layer and registers all handlers.
    """
    logger.info("Starting bot...")

    # Initialize Persistence (creates pals_pantry.db if missing)
    persistence_instance = SQLitePersistence()

    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    application.bot_data["persistence"] = persistence_instance

    # Register Handlers
    application.add_handler(set_owner_handler)
    application.add_handler(get_add_product_handler())
    general.register_handlers(application)
    customer.register_handlers(application)

    logger.info("Bot application built and handlers added. Starting polling...")

    application.run_polling()

    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    main()
