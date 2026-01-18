from abc import ABC, abstractmethod
from typing import Any, Optional  # For type hinting list[dict[str, Any]]


class AbstractPantryPersistence(ABC):
    """
    Abstract base class defining the interface for persistence operations.
    """

    @abstractmethod
    async def get_bot_owner(self) -> int | None:
        """
        Retrieves the user ID of the bot owner.

        Returns:
            int | None: The user ID of the bot owner, or None if not set.
        """
        pass

    @abstractmethod
    async def set_bot_owner(self, user_id: int) -> bool:
        """
        Sets the bot owner to the given user ID.
        This method should ideally only allow setting the owner if one is not already set.

        Args:
            user_id (int): The user ID to set as the bot owner.

        Returns:
            bool: True if the owner was successfully set (e.g., was not previously set),
                  False otherwise (e.g., if an owner was already set).
        """
        pass

    @abstractmethod
    async def is_owner_set(self) -> bool:
        """
        Checks if a bot owner has been set.

        Returns:
            bool: True if an owner is set, False otherwise.
        """
        pass

    # --- Product Management Methods ---
    @abstractmethod
    async def add_product(self, product_data: dict[str, Any]) -> str | None:
        """
        Adds a new product to the pantry/shop.

        Args:
            product_data (dict[str, Any]): A dictionary containing product details
                                           (e.g., name, price, description, category,
                                            quantity, image_file_id).
                                           Should also include owner_id for association.

        Returns:
            str | None: The ID of the newly created product, or None if failed.
        """
        pass

    @abstractmethod
    async def get_product(self, product_id: str) -> dict[str, Any] | None:
        """
        Retrieves a specific product by its ID.

        Args:
            product_id (str): The ID of the product.

        Returns:
            dict[str, Any] | None: The product data, or None if not found.
        """
        pass

    @abstractmethod
    async def get_all_products(self) -> list[dict[str, Any]]:
        """
        Retrieves all products.

        Returns:
            list[dict[str, Any]]: A list of all products.
        """
        pass

    @abstractmethod
    async def get_products_by_category(
        self, category_name: str
    ) -> list[dict[str, Any]]:
        """
        Retrieves all products belonging to a specific category.

        Args:
            category_name (str): The name of the category.

        Returns:
            list[dict[str, Any]]: A list of products in that category.
        """
        pass

    @abstractmethod
    async def get_all_categories(self) -> list[str]:
        """
        Retrieves a list of all unique category names.

        Returns:
            list[str]: A list of unique category names.
        """
        pass

    @abstractmethod
    async def update_product(
        self, product_id: str, product_data: dict[str, Any]
    ) -> bool:
        """
        Updates an existing product.

        Args:
            product_id (str): The ID of the product to update.
            product_data (dict[str, Any]): A dictionary with the product fields to update.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        pass

    @abstractmethod
    async def delete_product(self, product_id: str) -> bool:
        """
        Deletes a product.

        Args:
            product_id (str): The ID of the product to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        pass

    @abstractmethod
    async def update_product_stock(
        self, product_id: str, quantity_change: int
    ) -> int | None:
        """
        Updates the stock quantity of a product.
        A positive quantity_change increases stock, negative decreases.

        Args:
            product_id (str): The ID of the product.
            quantity_change (int): The amount to change the stock by (e.g., -1 for a sale).

        Returns:
            int | None: The new stock quantity if successful, None otherwise.
        """
        pass

    # --- Cart Management Methods ---
    @abstractmethod
    async def add_to_cart(self, user_id: int, product_id: str, quantity: int) -> Optional[int]:
        """
        Adds a product to the user's cart.

        Args:
            user_id (int): The ID of the user.
            product_id (str): The ID of the product to add.
            quantity (int): The quantity to add.

        Returns:
            Optional[int]: The new quantity on success, or None on failure.
        """
        pass

    @abstractmethod
    async def get_cart_items(self, user_id: int) -> dict[str, int]:
        """
        Retrieves the items in the user's cart.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict[str, int]: A dictionary mapping product IDs to quantities.
        """
        pass

    @abstractmethod
    async def clear_cart(self, user_id: int) -> bool:
        """
        Clears all items from the user's cart.

        Args:
            user_id (int): The ID of the user.

        Returns:
            bool: True if the cart was successfully cleared, False otherwise.
        """
        pass

    # --- Order Management Methods ---
    @abstractmethod
    async def create_order(self, user_id: int) -> Optional[str]:
        """
        Creates an order from the user's current cart. Returns the Order ID (UUID) if successful,
        or None if the cart is empty or stock is insufficient.
        """
        pass

    # @abstractmethod
    # async def get_order(self, order_id: str) -> dict[str, Any] | None:
    #     pass
    #
    # @abstractmethod
    # async def update_order_status(self, order_id: str, new_status: str) -> bool:
    #     pass
    #
    # @abstractmethod
    # async def get_user_orders(self, user_id: int) -> list[dict[str, Any]]:
    #     pass
    #
    # @abstractmethod
    # async def get_all_orders_for_owner(self) -> list[dict[str, Any]]: # Assuming single owner model
    #     pass
