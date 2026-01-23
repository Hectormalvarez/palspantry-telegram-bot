class Strings:
    class General:
        @staticmethod
        def welcome_user(name: str) -> str:
            return f"Welcome back, {name}!"

    class Cart:
        EMPTY = "Your cart is empty."