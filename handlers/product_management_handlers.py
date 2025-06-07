import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from persistence.abstract_persistence import AbstractPantryPersistence
from handlers.owner_handlers import owner_only_command # Import owner_only_command

logger = logging.getLogger(__name__)

async def my_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lists all products added by the owner."""
    if not await owner_only_command(update, context):
        return ConversationHandler.END

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    products = await persistence.get_all_products()

    if not products:
        await update.message.reply_text("You have not added any products yet.")
        logger.info(f"Owner {update.effective_user.id} requested /myproducts, but no products found.")
    else:
        message_parts = ["Your Products:\n\n"]
        for product in products:
            message_parts.append(
                f"Name: {product['name']}\n"
                f"Description: {product['description']}\n"
                f"Price: {product['price']:.2f}\n"
                f"Quantity: {product['quantity']}\n\n"
            )
        full_message = "".join(message_parts).strip()
        await update.message.reply_text(full_message)
        logger.info(f"Owner {update.effective_user.id} requested /myproducts. Listed {len(products)} products.")
    
    return ConversationHandler.END
