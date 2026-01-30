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

    class Cart:
        EMPTY = "Your cart is empty."
