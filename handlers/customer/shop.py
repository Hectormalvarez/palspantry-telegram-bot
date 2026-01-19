import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from persistence.abstract_persistence import AbstractPantryPersistence
from handlers.utils import schedule_deletion


logger = logging.getLogger(__name__)


async def shop_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry point: /shop or /menu."""
    # If this is called from a callback (Back button), we use edit_message_text
    # If called from a command (/shop), we use reply_text
    is_callback = bool(update.callback_query)

    if is_callback:
        # If we are coming 'back' from a photo view, we must delete the photo and send new text
        # Checks if the message we are replacing was a photo
        if update.callback_query.message.photo:
            await update.callback_query.message.delete()
            # Send new text message
            await _send_category_menu(update, context, send_new=True)
            return

    await _send_category_menu(update, context, send_new=not is_callback)

    if update.message:
        schedule_deletion(context, update.effective_chat.id, update.message.message_id, delay=3.0)


async def _send_category_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE, send_new: bool = False
):
    """Helper to render the category list."""
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    categories = await persistence.get_all_categories()

    if not categories:
        text = "The shop is currently empty. Please check back later!"
        if send_new:
            # Check if there is a message to reply to (command vs callback)
            if update.message:
                await update.message.reply_text(text)
            else:
                await update.effective_chat.send_message(text)
        else:
            await update.callback_query.edit_message_text(text)
        return

    keyboard = []
    for category in categories:
        keyboard.append(
            [InlineKeyboardButton(category, callback_data=f"category_{category}")]
        )
    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_shop")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "Welcome to PalsPantry! Select a category:"

    if send_new:
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id=chat_id, text=text, reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            text=text, reply_markup=reply_markup
        )


async def handle_category_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()

    # If we are coming back from a Product Detail (Photo), we need to delete the photo and send text
    if query.message.photo:
        await query.message.delete()
        category_name = context.matches[0].group(1)

        await _send_product_list(update, context, category_name, send_new=True)
        return

    # Normal text-to-text navigation
    category_name = context.matches[0].group(1)
    await _send_product_list(update, context, category_name, send_new=False)


async def _send_product_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    category_name: str,
    send_new: bool,
):
    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    products = await persistence.get_products_by_category(category_name)

    if not products:
        text = "No products here."
        if send_new:
            await update.effective_chat.send_message(text)
        else:
            await update.callback_query.edit_message_text(text)
        return

    keyboard = []
    for product in products:
        button_text = f"{product['name']} (${product['price']:.2f})"
        keyboard.append(
            [
                InlineKeyboardButton(
                    button_text, callback_data=f"product_{product['id']}"
                )
            ]
        )

    # Navigation
    keyboard.append(
        [
            InlineKeyboardButton(
                "<< Back to Categories", callback_data="navigate_to_categories"
            ),
            InlineKeyboardButton("❌ Close", callback_data="close_shop"),
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"<b>{category_name}</b>"

    if send_new:
        await update.effective_chat.send_message(
            text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )
    else:
        await update.callback_query.edit_message_text(
            text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )


async def handle_product_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Displays product details. Switches to Photo message if image exists."""
    query = update.callback_query
    await query.answer()
    product_id = context.matches[0].group(1)

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    product = await persistence.get_product(product_id)

    if not product:
        await query.edit_message_text("Product not found.")
        return

    # Prepare Content
    caption = (
        f"<b>{product['name']}</b>\n"
        f"<i>{product.get('description', '')}</i>\n\n"
        f"Price: <b>${product['price']:.2f}</b>\n"
        f"Stock: {product['quantity']} available"
    )

    category = product.get("category", "Products")

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 Add to Cart", callback_data=f"add_to_cart_{product_id}"
            )
        ],
        [
            InlineKeyboardButton(
                f"<< Back to {category}",
                callback_data=f"navigate_to_products_{category}",
            ),
            InlineKeyboardButton("❌ Close", callback_data="close_shop"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    image_id = product.get("image_file_id")

    # LOGIC:
    # 1. We are currently viewing a Text Message (Product List).
    # 2. We want to show details.
    # 3. If Image exists -> Delete Text, Send Photo.
    # 4. If No Image -> Edit Text.

    if image_id:
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=image_id,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
    else:
        # Fallback for products with no image
        await query.edit_message_text(
            text=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )


async def handle_add_to_cart(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    # We don't need to edit the message, just pop up a notification
    product_id = context.matches[0].group(1)

    persistence: AbstractPantryPersistence = context.bot_data["persistence"]
    product = await persistence.get_product(product_id)

    if not product:
        await query.answer("Product no longer available.", show_alert=True)
        return

    user_id = update.effective_user.id
    new_quantity = await persistence.add_to_cart(user_id=user_id, product_id=product_id, quantity=1)

    if new_quantity:
        await query.answer(f"{product['name']} added to cart! (Total: {new_quantity})")
    else:
        await query.answer("Error adding to cart. Please try again.", show_alert=True)


async def handle_close_shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    message_id_to_delete = None

    # Check if we are closing a photo message
    if query.message.photo:
        await query.message.delete()
        sent_msg = await context.bot.send_message(
            chat_id=chat_id, text="Shop closed. See you soon!"
        )
        message_id_to_delete = sent_msg.message_id
    else:
        await query.edit_message_text("Shop closed. See you soon!", reply_markup=None)
        message_id_to_delete = query.message.message_id

    # Schedule deletion for 5 seconds later
    if message_id_to_delete:
        schedule_deletion(context, chat_id, message_id_to_delete, delay=5.0)


async def handle_back_to_categories(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles 'Back to Categories'. Compatible with both Photo and Text origins."""
    query = update.callback_query
    await query.answer()
    await shop_start(update, context)


# --- Handler Registration ---
# Note: We need to register these in bot_main.py, but using the variables exported here.

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
# Regex Updated to capture the category name for the Back button logic
back_to_products_handler = CallbackQueryHandler(
    handle_category_selection, pattern="^navigate_to_products_(.+)"
)
shop_home_callback_handler = CallbackQueryHandler(shop_start, pattern="^shop_start$")
