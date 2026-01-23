import pytest

from resources.strings import Strings


def test_string_structure():
    assert Strings.Cart.EMPTY == "Your cart is empty."
    assert Strings.General.welcome_user("Alice") == "Welcome back, Alice!"
