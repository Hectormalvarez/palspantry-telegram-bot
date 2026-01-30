import logging

from telegram.ext import ApplicationBuilder, CommandHandler

import config
from handlers import general, customer, owner, product
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
    owner.register_handlers(application)
    product.register_handlers(application)
    general.register_handlers(application)
    customer.register_handlers(application)

    logger.info("Bot application built and handlers added. Starting polling...")

    application.run_polling()

    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    main()
