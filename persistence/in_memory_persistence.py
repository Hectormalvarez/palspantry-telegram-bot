from typing import Any
import uuid  # For type hinting
import logging

from .abstract_persistence import AbstractPantryPersistence


logger = logging.getLogger(__name__)


class InMemoryPersistence(AbstractPantryPersistence):
    """
    In-memory implementation of the persistence layer.
    Stores data in instance variables. Data is lost when the bot restarts.
    """

    def __init__(self):
        self._bot_owner_id: int | None = None
        self._products: dict[str, dict[str, Any]] = {}
        self._next_product_int_id: int = 1

        logger.info(
            "InMemoryPersistence initialized (attributes for products and owner are set)."
        )
        logger.debug(
            f"InMemoryPersistence: Initial state - Owner: {self._bot_owner_id}, "
            f"Products: {len(self._products)}"
        )

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

    # --- Product Management Implementations ---
    async def add_product(self, product_data: dict[str, Any]) -> str | None:
        product_id = str(uuid.uuid4())  # Using UUID for universally unique IDs
        self._next_product_int_id += 1

        # Ensure essential fields exist, though ConversationHandler should gather them
        if not all(
            k in product_data for k in ["name", "price", "quantity", "category"]
        ):
            logger.error(
                f"Missing essential product data for add_product: {product_data}"
            )
            return None

        self._products[product_id] = {"id": product_id, **product_data}
        logger.info(f"Product added with ID {product_id}: {product_data.get('name')}")
        return product_id

    async def get_product(self, product_id: str) -> dict[str, Any] | None:
        product = self._products.get(product_id)
        logger.debug(
            f"Attempting to get product with ID {product_id}. Found: {bool(product)}"
        )
        return product

    async def get_all_products(self) -> list[dict[str, Any]]:
        all_prods = list(self._products.values())
        logger.debug(f"Retrieving all products. Count: {len(all_prods)}")
        return all_prods

    async def get_products_by_category(
        self, category_name: str
    ) -> list[dict[str, Any]]:
        cat_prods = [
            prod
            for prod in self._products.values()
            if prod.get("category", "").lower() == category_name.lower()
        ]
        logger.debug(
            f"Retrieving products for category '{category_name}'. Count: {len(cat_prods)}"
        )
        return cat_prods

    async def get_all_categories(self) -> list[str]:
        categories = sorted(
            list(
                set(
                    prod.get("category", "Uncategorized")
                    for prod in self._products.values()
                    if prod.get("category")
                )
            )
        )
        logger.debug(f"Retrieving all categories. Found: {categories}")
        return categories

    async def update_product(
        self, product_id: str, product_data: dict[str, Any]
    ) -> bool:
        if product_id in self._products:
            # Only update fields that are provided in product_data
            for key, value in product_data.items():
                self._products[product_id][key] = value
            logger.info(f"Product {product_id} updated with data: {product_data}")
            return True
        logger.warning(f"Attempted to update non-existent product ID: {product_id}")
        return False

    async def delete_product(self, product_id: str) -> bool:
        if product_id in self._products:
            del self._products[product_id]
            logger.info(f"Product {product_id} deleted.")
            return True
        logger.warning(f"Attempted to delete non-existent product ID: {product_id}")
        return False

    async def update_product_stock(
        self, product_id: str, quantity_change: int
    ) -> int | None:
        if product_id in self._products:
            current_stock = self._products[product_id].get("quantity", 0)
            new_stock = current_stock + quantity_change
            if new_stock < 0:
                logger.warning(
                    f"Stock for product {product_id} cannot go below zero (attempted {new_stock}). Not updated."
                )
                return None  # Or current_stock, or raise error

            self._products[product_id]["quantity"] = new_stock
            logger.info(
                f"Stock for product {product_id} changed by {quantity_change} to {new_stock}."
            )
            return new_stock
        logger.warning(
            f"Attempted to update stock for non-existent product ID: {product_id}"
        )
        return None

    # --- Order Management Implementations (to be added later) ---
