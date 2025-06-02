# FILE: persistence/in_memory_persistence.py
from .abstract_persistence import AbstractPantryPersistence
import logging

logger = logging.getLogger(__name__)


class InMemoryPersistence(AbstractPantryPersistence):
    """
    In-memory implementation of the persistence layer.
    Stores data in instance variables. Data is lost when the bot restarts.
    """

    def __init__(self):
        self._bot_owner_id: int | None = None
        # In the future, pantry items could be stored here, e.g.:
        # self._pantry_items: dict[int, dict[str, int]] = {} # user_id -> {item_name: quantity}
        logger.info("InMemoryPersistence initialized.")

    async def get_bot_owner(self) -> int | None:
        logger.debug(
            f"InMemoryPersistence: Getting bot owner. Current value: {self._bot_owner_id}"
        )
        return self._bot_owner_id

    async def set_bot_owner(self, user_id: int) -> bool:
        if self._bot_owner_id is None:
            self._bot_owner_id = user_id
            logger.info(f"InMemoryPersistence: Bot owner set to {user_id}.")
            return True
        logger.warning(
            f"InMemoryPersistence: Attempted to set owner to {user_id}, but owner already set to {self._bot_owner_id}."
        )
        return False  # Owner was already set, or some other logic preventing update

    async def is_owner_set(self) -> bool:
        is_set = self._bot_owner_id is not None
        logger.debug(f"InMemoryPersistence: Checking if owner is set. Result: {is_set}")
        return is_set

    # Future pantry-related method implementations:
    # async def add_pantry_item(self, user_id: int, item_name: str, quantity: int = 1) -> None:
    #     if user_id not in self._pantry_items:
    #         self._pantry_items[user_id] = {}
    #     self._pantry_items[user_id][item_name] = self._pantry_items[user_id].get(item_name, 0) + quantity
    #     logger.info(f"Item '{item_name}' (quantity: {quantity}) added/updated for user {user_id}.")

    # async def get_pantry_items(self, user_id: int) -> list:
    #     items = self._pantry_items.get(user_id, {})
    #     logger.debug(f"Retrieving items for user {user_id}: {items}")
    #     return [{"name": name, "quantity": qty} for name, qty in items.items()] # Example format

    # async def remove_pantry_item(self, user_id: int, item_name: str) -> bool:
    #     if user_id in self._pantry_items and item_name in self._pantry_items[user_id]:
    #         del self._pantry_items[user_id][item_name]
    #         logger.info(f"Item '{item_name}' removed for user {user_id}.")
    #         return True
    #     logger.warning(f"Item '{item_name}' not found for user {user_id} during removal attempt.")
    #     return False

    # async def update_pantry_item_quantity(self, user_id: int, item_name: str, new_quantity: int) -> bool:
    #     if user_id in self._pantry_items and item_name in self._pantry_items[user_id]:
    #         if new_quantity > 0:
    #             self._pantry_items[user_id][item_name] = new_quantity
    #             logger.info(f"Item '{item_name}' quantity updated to {new_quantity} for user {user_id}.")
    #         else: # If new quantity is 0 or less, remove the item
    #             del self._pantry_items[user_id][item_name]
    #             logger.info(f"Item '{item_name}' removed for user {user_id} due to zero quantity update.")
    #         return True
    #     logger.warning(f"Item '{item_name}' not found for user {user_id} during quantity update attempt.")
    #     return False
