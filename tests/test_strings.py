import pytest

from resources.strings import Strings


def test_cart_strings():
    """Test cart-related string constants."""
    assert Strings.Cart.EMPTY == "Your cart is empty."


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
