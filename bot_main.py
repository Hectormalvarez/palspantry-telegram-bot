import os
from telegram.ext import Application, CommandHandler, ContextTypes, TypeHandler, MessageHandler, filters
from telegram import Update
from database import create_tables, add_or_update_user, get_all_products # Import create_tables, add_or_update_user, and get_all_products

# Global variable to store the bot owner's user ID
BOT_OWNER = None

async def record_user_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Records user interaction by adding/updating them in the database."""
    if update.effective_user:
        user = update.effective_user
        telegram_id = user.id
        first_name = user.first_name
        # In some cases, first_name might be None, provide a default or handle appropriately
        if first_name is None:
            first_name = "User" # Default name if first_name is not available
        
        add_or_update_user(telegram_id, first_name)
        # No reply needed here as this is a background task for every interaction

async def set_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global BOT_OWNER
    user_id = update.effective_user.id
    if BOT_OWNER is None:
        BOT_OWNER = user_id
        await update.message.reply_text(f"You are now the owner of this bot.")
    else:
        await update.message.reply_text("An owner has already been set.")

async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds a new product to the Product table. Only the bot owner can use this command."""
    global BOT_OWNER
    user_id = update.effective_user.id

    if BOT_OWNER is None or user_id != BOT_OWNER:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    try:
        # Parse the command arguments
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /add_product <name> <price> <category>")
            return

        name = args[0]
        try:
            price = float(args[1])
        except ValueError:
            await update.message.reply_text("Invalid price. Price must be a number.")
            return
        category = args[2]

        # Add the product to the database
        from database import add_product  # Import the add_product function
        if add_product(name, price, category):
            await update.message.reply_text(f"Product '{name}' added successfully.")
        else:
            await update.message.reply_text(f"Failed to add product '{name}'. Product with this name may already exist.")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lists all products in the Product table. Only the bot owner can use this command."""
    global BOT_OWNER
    user_id = update.effective_user.id

    if BOT_OWNER is None or user_id != BOT_OWNER:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    try:
        products = get_all_products()
        
        if not products:
            await update.message.reply_text("No products found.")
            return

        # Format the product list
        product_list = "Current Products:\n"
        for product in products:
            product_list += f"- {product['name']} (ID: {product['id']}): ${product['price']:.2f} | Category: {product['category'] or 'N/A'}\n"
        
        await update.message.reply_text(product_list)

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    if update.effective_user:
        await update.message.reply_text(f"Hello {update.effective_user.first_name}! Welcome to Pal's Pantry Bot.")
    else:
        await update.message.reply_text("Hello! Welcome to Pal's Pantry Bot.")

def main() -> None:
    """Start the bot."""
    # Initialize database tables
    create_tables()

    # Get the bot token from the environment variable
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("Error: BOT_TOKEN environment variable not set.")
        return

    # Create the application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # Add the user interaction recorder handler.
    # Group -1 ensures it runs before other handlers (default group is 0).
    # block=False ensures it doesn't stop other handlers from processing the update.
    application.add_handler(TypeHandler(Update, record_user_interaction, block=False), group=-1)

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_owner", set_owner))
    application.add_handler(CommandHandler("add_product", add_product))
    application.add_handler(CommandHandler("list_products", list_products))

    # You might want a generic message handler for other interactions if needed
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, some_other_function))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
