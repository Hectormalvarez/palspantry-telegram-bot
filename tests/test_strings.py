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
