from abc import ABC, abstractmethod


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

    # Future pantry-related methods will be added here:
    # @abstractmethod
    # async def add_pantry_item(self, user_id: int, item_name: str, quantity: int = 1) -> None:
    #     pass
    #
    # @abstractmethod
    # async def get_pantry_items(self, user_id: int) -> list: # Define what a pantry item looks like
    #     pass
    #
    # @abstractmethod
    # async def remove_pantry_item(self, user_id: int, item_name: str) -> bool:
    #     pass
    #
    # @abstractmethod
    # async def update_pantry_item_quantity(self, user_id: int, item_name: str, new_quantity: int) -> bool:
    #     pass
