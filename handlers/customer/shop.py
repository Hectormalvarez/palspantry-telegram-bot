import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler

from persistence.abstract_persistence import AbstractPantryPersistence


logger = logging.getLogger(__name__)


async def shop_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /shop command. Displays a list of product categories to the user.
    """
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    categories = await persistence.get_all_categories()

    if not categories:
        await update.message.reply_text(
            "The shop is currently empty. Please check back later!"
        )
        return

    keyboard = []
    for category in categories:
        # Each button is on its own row
        keyboard.append(
            [InlineKeyboardButton(category, callback_data=f"category_{category}")]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to the shop! Please select a category to browse:",
        reply_markup=reply_markup,
    )


async def handle_category_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handles a user clicking a category button.
    Displays the products in the selected category as clickable buttons.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    # The category name is captured from the regex in the CallbackQueryHandler
    category_name = context.matches[0].group(1)

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    products = await persistence.get_products_by_category(category_name)

    if not products:
        await query.edit_message_text(
            text="There are currently no products available in this category."
        )
        return

    # Build an InlineKeyboardMarkup with a button for each product
    keyboard = []
    for product in products:
        button_text = f"{product['name']} (${product['price']:.2f})"
        # The callback_data will include the product ID for the next step
        callback_data = f"product_{product.get('id')}"
        keyboard.append(
            [InlineKeyboardButton(button_text, callback_data=callback_data)]
        )

    # Add the navigation row
    navigation_row = [
        InlineKeyboardButton(
            "<< Back to Categories", callback_data="navigate_to_categories"
        ),
        InlineKeyboardButton("❌ Close", callback_data="close_shop"),
    ]
    keyboard.append(navigation_row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edit the message to show the new header and the product buttons
    await query.edit_message_text(
        text=f"Products in {category_name}:",
        reply_markup=reply_markup,
    )


async def handle_product_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles a user clicking a product button, showing product details."""
    query = update.callback_query
    await query.answer()

    # Extract the product_id from the captured regex group
    product_id = context.matches[0].group(1)

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    product = await persistence.get_product(product_id)

    if not product:
        await query.edit_message_text(text="Sorry, this product could not be found.")
        return

    # Format the detailed message
    text = (
        f"Name: {product['name']}\n"
        f"Description: {product['description']}\n"
        f"Price: ${product['price']:.2f}"
    )

    category_name = product.get("category", "Products")  # Safely get category

    # Create the "Add to Cart" button
    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 Add to Cart", callback_data=f"add_to_cart_{product_id}"
            )
        ],
        [
            InlineKeyboardButton(
                f"<< Back to {category_name} Products",
                callback_data=f"navigate_to_products_{category_name}",
            ),
            InlineKeyboardButton("❌ Close", callback_data="close_shop"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup)


async def handle_add_to_cart(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles the 'Add to Cart' button click."""
    query = update.callback_query
    product_id = context.matches[0].group(1)

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    product = await persistence.get_product(product_id)

    # Handle case where product might not exist anymore
    if not product:
        await query.answer(
            "Sorry, this product is no longer available.", show_alert=True
        )
        return

    # Get the user's cart from their session, creating it if it's the first time
    cart = context.user_data.setdefault("cart", {})

    # Add the item to the cart or increment its quantity
    current_quantity = cart.get(product_id, 0)
    cart[product_id] = current_quantity + 1

    logger.info(f"User {update.effective_user.id} updated cart: {cart}")

    # Send a small confirmation pop-up to the user
    await query.answer(text=f"{product['name']} added to cart!")


async def handle_close_shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the 'close_shop' callback by ending the interaction."""

    query = update.callback_query

    # Acknowledge the button press
    await query.answer()
    await query.edit_message_text(
        # This removes the keyboard
        text="Shopping session ended.",
        reply_markup=None,
    )


async def handle_back_to_categories(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles the 'Back to Categories' button click by re-displaying the categorie list."""
    query = update.callback_query
    await query.answer()

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    categories = await persistence.get_all_categories()

    keyboard = []
    for category in categories:
        keyboard.append(
            [InlineKeyboardButton(category, callback_data=f"category_{category}")]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Welcome to the shop! Please select a category to browse:",
        reply_markup=reply_markup,
    )


shop_start_handler = CommandHandler("shop", shop_start)


category_selection_handler = CallbackQueryHandler(
    handle_category_selection, pattern="^category_(.+)"
)


product_selection_handler = CallbackQueryHandler(
    handle_product_selection, pattern="^product_(.+)"
)


add_to_cart_handler = CallbackQueryHandler(
    handle_add_to_cart, pattern="^add_to_cart_(.+)"
)


close_shop_handler = CallbackQueryHandler(handle_close_shop, pattern="^close_shop$")


back_to_categories_handler = CallbackQueryHandler(
    handle_back_to_categories, pattern="^navigate_to_categories$"
)


back_to_products_handler = CallbackQueryHandler(
    handle_category_selection, pattern="^navigate_to_products_(.+)"
)
