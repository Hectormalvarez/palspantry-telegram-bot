import logging
from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ApplicationBuilder,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

# Import configuration (this will also initialize logging)
import config

# Import persistence layer
from persistence.in_memory_persistence import InMemoryPersistence
from persistence.abstract_persistence import (
    AbstractPantryPersistence,
)  # For type hinting

# Import owner handlers
from handlers.owner_handlers import (
    set_owner,
    add_product_start,
    PRODUCT_NAME,
    PRODUCT_DESCRIPTION,
    PRODUCT_PRICE,
    PRODUCT_QUANTITY,
    PRODUCT_CATEGORY,
    PRODUCT_CONFIRMATION,
    cancel_add_product,
    received_product_name,
    received_product_description,
    received_product_price,
    received_product_quantity,
    received_product_category,
    handle_product_save_confirmed,
    handle_product_edit_choice,
    handle_product_cancel_from_confirmation,
)
from handlers.product_management_handlers import my_products


# Get a logger for this module
logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")

    # Create an instance of our persistence layer
    persistence_instance = InMemoryPersistence()

    # Use ApplicationBuilder for more explicit setup
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    application.bot_data["persistence"] = persistence_instance

    # Conversation handler for adding products
    add_product_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addproduct", add_product_start)],
        states={
            PRODUCT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_product_name),
            ],
            PRODUCT_DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, received_product_description
                )
            ],
            PRODUCT_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_product_price)
            ],
            PRODUCT_QUANTITY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, received_product_quantity
                )
            ],
            PRODUCT_CATEGORY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, received_product_category
                )
            ],
            PRODUCT_CONFIRMATION: [
                CallbackQueryHandler(
                    handle_product_save_confirmed, pattern="^product_confirm_save$"
                ),
                CallbackQueryHandler(
                    handle_product_edit_choice, pattern="^product_confirm_edit$"
                ),
                CallbackQueryHandler(
                    handle_product_cancel_from_confirmation,
                    pattern="^product_confirm_cancel$",
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_add_product)],
    )

    # Add command handler
    application.add_handler(CommandHandler("set_owner", set_owner))
    application.add_handler(add_product_conv_handler)
    application.add_handler(CommandHandler("myproducts", my_products))

    logger.info("Bot application built and handlers added. Starting polling...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    main()
