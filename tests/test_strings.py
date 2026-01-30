import pytest

from resources.strings import Strings


def test_cart_strings():
    """Test cart-related string constants."""
    assert Strings.Cart.EMPTY == "Your cart is empty."
    assert Strings.Cart.CLEAR_BTN == "Clear Cart"
    assert Strings.Cart.CLEARED == "Cart cleared."
    assert Strings.Cart.CHECKOUT_ERROR_EMPTY == "Cannot place order. Is your cart empty?"
    assert Strings.Cart.RECEIPT_HEADER == "✅ Order Placed Successfully!"
    assert Strings.Cart.RECEIPT_FOOTER == "Thank you!"

    # Test cart methods
    assert Strings.Cart.item_line("Apple", 2, 1.50, 3.00) == "- Apple (2 x $1.50) = $3.00"
    assert Strings.Cart.total_line(15.75) == "Total: $15.75"
    assert Strings.Cart.receipt_item("Banana", 3, 0.80) == "- Banana x 3 @ $0.80"
    assert Strings.Cart.receipt_total(12.50) == "<b>Total: $12.50</b>"


def test_general_strings():
    """Test general string methods and constants."""
    # Test welcome messages
    assert Strings.General.welcome_new_user("Alice") == "Welcome, Alice! \n\nI am the PalsPantry Bot. I can help you browse our inventory and place orders."
    assert Strings.General.welcome_returning_user("Bob") == "Welcome back, Bob!\n\nYou have items in your cart."
    
    # Test button labels
    assert Strings.General.SHOP_NOW_BTN == "🛍️ Shop Now"
    assert Strings.General.CONTINUE_SHOPPING_BTN == "🛍️ Continue Shopping"
    assert Strings.General.CHECKOUT_BTN == "🛒 Checkout"


def test_help_strings():
    """Test help command string."""
    help_message = Strings.Help.MESSAGE
    assert "Available commands:" in help_message
    assert "/shop" in help_message
    assert "/help" in help_message
    assert "/start" in help_message


def test_error_strings():
    """Test error message strings."""
    assert Strings.Error.UNKNOWN_COMMAND == "Sorry, I didn't understand that. Please use /start to begin or /shop to browse the menu."


def test_owner_strings():
    """Test owner-related string constants."""
    assert Strings.Owner.SET_SUCCESS == "You are now the owner of this bot."
    assert Strings.Owner.SET_FAILED == "Could not set owner at this time. An owner might already be registered."
    assert Strings.Owner.ALREADY_SET == "An owner has already been set."
    assert Strings.Owner.NOT_OWNER == "Sorry, this command is only for the bot owner."


def test_product_strings():
    """Test product-related string constants and methods."""
    # Test basic string constants
    assert Strings.Product.START_ADD == "Let's add a new product! First, what is the product's name?"
    assert Strings.Product.ASK_PRICE == "Description noted.\n\nNow, what's the price? (e.g., 10.99 or 5)"
    assert Strings.Product.ASK_IMAGE == "Category set.\n\nFinally, please send a photo of the product.\nOr type /skip if you don't want to add an image."
    assert Strings.Product.NO_IMAGE_ADDED == "No image added."
    
    # Test error strings
    assert Strings.Product.ERR_EMPTY_NAME == "Product name cannot be empty. Please enter a name, or /cancel."
    assert Strings.Product.ERR_EMPTY_DESC == "Description cannot be empty. Please enter a description, or /cancel."
    assert Strings.Product.ERR_INVALID_PRICE == "Invalid price. Please enter a positive number (e.g. 10.99), or /cancel."
    assert Strings.Product.ERR_INVALID_QTY == "Invalid quantity. Please enter a whole positive number, or /cancel."
    assert Strings.Product.ERR_EMPTY_CATEGORY == "Category cannot be empty. Please enter a category, or /cancel."
    assert Strings.Product.ERR_DATA_LOST == "Error: Data lost. Please try again."
    assert Strings.Product.ERR_DB_SAVE == "❌ Database error. Could not save."
    
    # Test result strings
    assert Strings.Product.CANCELLED == "Product addition cancelled."
    assert Strings.Product.SUCCESS_ADDED == "✅ Product '{name}' added!"
    
    # Test button strings
    assert Strings.Product.BTN_CONFIRM == "✅ Confirm & Save"
    assert Strings.Product.BTN_CANCEL == "❌ Cancel"
    
    # Test formatted strings
    assert Strings.Product.ASK_DESCRIPTION.format(name="Test Product") == "Name set to 'Test Product'.\n\nNow, please enter a description."
    assert Strings.Product.ASK_QUANTITY.format(price=19.99) == "Price set to $19.99.\n\nHow many units are available? (e.g., 10)"
    assert Strings.Product.ASK_CATEGORY.format(qty=5) == "Quantity set to 5.\n\nNow, please specify a category (e.g. 'Dairy')."
    assert Strings.Product.SUCCESS_ADDED.format(name="Test Product") == "✅ Product 'Test Product' added!"
    
    # Test confirm_summary method
    summary = Strings.Product.confirm_summary(
        name="Test Product",
        desc="Test Description",
        price=19.99,
        qty=5,
        cat="Dairy",
        has_image=True
    )
    expected_summary = (
        "<b>Confirm New Product:</b>\n\n"
        "<b>Name:</b> Test Product\n"
        "<b>Desc:</b> Test Description\n"
        "<b>Price:</b> $19.99\n"
        "<b>Qty:</b> 5\n"
        "<b>Cat:</b> Dairy\n"
        "<b>Image:</b> Yes\n\n"
        "Save this product?"
    )
    assert summary == expected_summary
