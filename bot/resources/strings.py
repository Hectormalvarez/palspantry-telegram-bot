class Strings:
    class General:
        @staticmethod
        def welcome_new_user(name: str) -> str:
            return f"Welcome, {name}! \n\nI am the PalsPantry Bot. I can help you browse our inventory and place orders."

        @staticmethod
        def welcome_returning_user(name: str) -> str:
            return f"Welcome back, {name}!\n\nYou have items in your cart."

        SHOP_NOW_BTN = "🛍️ Shop Now"
        CONTINUE_SHOPPING_BTN = "🛍️ Continue Shopping"
        CHECKOUT_BTN = "🛒 Checkout"

    class Help:
        MESSAGE = """
<b>Available commands:</b>

🛒 <b>Shopping</b>
/shop - Browse our inventory
/cart - View your shopping cart
/checkout - Place your order

⚙️ <b>General</b>
/start - Welcome message
/help - Show this message

🔑 <b>Owner Only</b>
/addproduct - Add a new item to the shop
/set_owner - Claim bot ownership
"""

    class Error:
        UNKNOWN_COMMAND = "Sorry, I didn't understand that. Please use /start to begin or /shop to browse the menu."

    class Owner:
        SET_SUCCESS = "You are now the owner of this bot."
        SET_FAILED = (
            "Could not set owner at this time. An owner might already be registered."
        )
        ALREADY_SET = "An owner has already been set."
        NOT_OWNER = "Sorry, this command is only for the bot owner."

    class Product:
        # Conversation Prompts
        START_ADD = "Let's add a new product! First, what is the product's name?"
        ASK_DESCRIPTION = "Name set to '{name}'.\n\nNow, please enter a description."
        ASK_PRICE = "Description noted.\n\nNow, what's the price? (e.g., 10.99 or 5)"
        ASK_QUANTITY = (
            "Price set to ${price:.2f}.\n\nHow many units are available? (e.g., 10)"
        )
        ASK_CATEGORY = (
            "Quantity set to {qty}.\n\nNow, please specify a category (e.g. 'Dairy')."
        )
        ASK_IMAGE = "Category set.\n\nFinally, please send a photo of the product.\nOr type /skip if you don't want to add an image."
        NO_IMAGE_ADDED = "No image added."

        # Errors & Validation
        ERR_EMPTY_NAME = (
            "Product name cannot be empty. Please enter a name, or /cancel."
        )
        ERR_EMPTY_DESC = (
            "Description cannot be empty. Please enter a description, or /cancel."
        )
        ERR_INVALID_PRICE = (
            "Invalid price. Please enter a positive number (e.g. 10.99), or /cancel."
        )
        ERR_INVALID_QTY = (
            "Invalid quantity. Please enter a whole positive number, or /cancel."
        )
        ERR_EMPTY_CATEGORY = (
            "Category cannot be empty. Please enter a category, or /cancel."
        )
        ERR_DATA_LOST = "Error: Data lost. Please try again."
        ERR_DB_SAVE = "❌ Database error. Could not save."

        # Results
        CANCELLED = "Product addition cancelled."
        SUCCESS_ADDED = "✅ Product '{name}' added!"

        # Buttons
        BTN_CONFIRM = "✅ Confirm & Save"
        BTN_CANCEL = "❌ Cancel"

        @staticmethod
        def confirm_summary(
            name: str, desc: str, price: float, qty: int, cat: str, has_image: bool
        ) -> str:
            return (
                "<b>Confirm New Product:</b>\n\n"
                f"<b>Name:</b> {name}\n"
                f"<b>Desc:</b> {desc}\n"
                f"<b>Price:</b> ${price:.2f}\n"
                f"<b>Qty:</b> {qty}\n"
                f"<b>Cat:</b> {cat}\n"
                f"<b>Image:</b> {'Yes' if has_image else 'No'}\n\n"
                "Save this product?"
            )

    class Shop:
        EMPTY = "The shop is currently empty. Please check back later!"
        CATEGORY_HEADER = "Welcome to PalsPantry! Select a category:"
        NO_PRODUCTS = "No products here."
        PRODUCT_NOT_FOUND = "Product not found."
        PRODUCT_UNAVAILABLE = "Product no longer available."
        ADD_ERROR = "Error adding to cart. Please try again."

        CLOSE_BTN = "❌ Close"
        BACK_TO_CATEGORIES_BTN = "<< Back to Categories"
        ADD_TO_CART_BTN = "🛒 Add to Cart"

        @staticmethod
        def category_title(category: str) -> str:
            return f"<b>{category}</b>"

        @staticmethod
        def back_to_category_btn(category: str) -> str:
            return f"<< Back to {category}"

        @staticmethod
        def product_button(name: str, price: float) -> str:
            return f"{name} (${price:.2f})"

        @staticmethod
        def product_caption(name: str, desc: str, price: float, stock: int) -> str:
            return (
                f"<b>{name}</b>\n"
                f"<i>{desc}</i>\n\n"
                f"Price: <b>${price:.2f}</b>\n"
                f"Stock: {stock} available"
            )

        @staticmethod
        def added_to_cart(name: str, total: int) -> str:
            return f"{name} added to cart! (Total: {total})"

    class Cart:
        EMPTY = "Your cart is empty."
        CLEAR_BTN = "Clear Cart"
        CLEARED = "Cart cleared."
        CHECKOUT_ERROR_EMPTY = "Cannot place order. Is your cart empty?"
        RECEIPT_HEADER = "✅ Order Placed Successfully!"
        RECEIPT_FOOTER = "Thank you!"

        @staticmethod
        def item_line(name: str, qty: int, price: float, total: float) -> str:
            return f"- {name} ({qty} x ${price:.2f}) = ${total:.2f}"

        @staticmethod
        def total_line(total: float) -> str:
            return f"Total: ${total:.2f}"

        @staticmethod
        def receipt_item(name: str, qty: int, price: float) -> str:
            return f"- {name} x {qty} @ ${price:.2f}"

        @staticmethod
        def receipt_total(total: float) -> str:
            return f"<b>Total: ${total:.2f}</b>"

    class Order:
        @staticmethod
        def notification_new(
            user_id: int, order_id: str, items_summary: str, total: float
        ) -> str:
            return (
                "🔔 New Order Received!\n"
                f"Customer: {user_id}\n"
                f"Order ID: {order_id}\n"
                f"{items_summary}\n"
                f"Total: ${total:.2f}"
            )
