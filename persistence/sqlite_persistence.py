"""
SQLite Persistence Layer for PalsPantry.

This module implements the storage interface using a local SQLite database.
It handles raw SQL execution, connection management, and data transformation.
"""

import sqlite3
import logging
import uuid
from typing import Any, Optional, List

from .abstract_persistence import AbstractPantryPersistence

logger = logging.getLogger(__name__)


class SQLitePersistence(AbstractPantryPersistence):
    """
    SQLite implementation of the persistence layer.

    Attributes:
        db_path (str): The file path to the SQLite database.
    """

    def __init__(self, db_path: str = "pals_pantry.db"):
        """
        Initializes the persistence layer and ensures the database schema exists.

        Args:
            db_path (str): Path to the .db file. Defaults to "pals_pantry.db".
        """
        self.db_path = db_path
        self._init_db()
        logger.info(f"SQLitePersistence initialized with DB: {self.db_path}")

    # --- Internal Helpers ---

    def _get_connection(self) -> sqlite3.Connection:
        """
        Creates a configured database connection.

        Returns:
            sqlite3.Connection: Connection object with row_factory set to sqlite3.Row.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_product(self, row: sqlite3.Row) -> dict[str, Any]:
        """
        Helper to transform a raw DB row into an app-friendly product dict.

        Args:
            row (sqlite3.Row): The raw database row.

        Returns:
            dict[str, Any]: Product dictionary with 'price' converted to float.
        """
        data = dict(row)
        # Centralized Price Conversion: Cents (Int) -> Dollars (Float)
        data["price"] = data["price_cents"] / 100.0
        return data

    def _execute_write(self, query: str, params: tuple = ()) -> bool:
        """
        Helper for INSERT/UPDATE/DELETE queries.

        Args:
            query (str): The SQL query string.
            params (tuple): The parameters to substitute into the query.

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        conn = self._get_connection()
        try:
            with conn:  # Context manager automatically commits if no error
                conn.execute(query, params)
            return True
        except sqlite3.Error as e:
            logger.error(f"DB Write Error: {e} | Query: {query}")
            return False
        finally:
            conn.close()

    def _execute_read_one(
        self, query: str, params: tuple = ()
    ) -> Optional[sqlite3.Row]:
        """
        Helper for SELECT queries expecting a single row.

        Args:
            query (str): The SQL query string.
            params (tuple): The parameters to substitute into the query.

        Returns:
            Optional[sqlite3.Row]: The row if found, else None.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        finally:
            conn.close()

    def _execute_read_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Helper for SELECT queries expecting multiple rows.

        Args:
            query (str): The SQL query string.
            params (tuple): The parameters to substitute into the query.

        Returns:
            List[sqlite3.Row]: A list of rows.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            conn.close()

    def _init_db(self) -> None:
        """
        Initializes the database schema if tables do not exist.
        Uses a raw script execution for multiple statements.
        """
        conn = self._get_connection()
        try:
            with conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS system_config (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    );

                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS products (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        price_cents INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        category TEXT,
                        image_file_id TEXT,
                        is_active INTEGER DEFAULT 1
                    );

                    CREATE TABLE IF NOT EXISTS cart_items (
                        user_id INTEGER,
                        product_id TEXT,
                        quantity INTEGER,
                        PRIMARY KEY (user_id, product_id),
                        FOREIGN KEY (product_id) REFERENCES products(id)
                    );

                    CREATE TABLE IF NOT EXISTS orders (
                        id TEXT PRIMARY KEY,
                        user_id INTEGER,
                        total_amount REAL,
                        status TEXT DEFAULT 'completed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS order_items (
                        order_id TEXT,
                        product_id TEXT,
                        quantity INTEGER,
                        unit_price REAL,
                        FOREIGN KEY(order_id) REFERENCES orders(id),
                        FOREIGN KEY(product_id) REFERENCES products(id)
                    );
                """
                )
        finally:
            conn.close()

    # --- Owner Management ---

    async def get_bot_owner(self) -> Optional[int]:
        """
        Retrieves the user ID of the bot owner.

        Returns:
            Optional[int]: The owner's user ID, or None if not set.
        """
        row = self._execute_read_one(
            "SELECT value FROM system_config WHERE key = 'owner_id'"
        )
        return int(row["value"]) if row else None

    async def set_bot_owner(self, user_id: int) -> bool:
        """
        Sets the bot owner if one is not already set.

        Args:
            user_id (int): The Telegram user ID to set as owner.

        Returns:
            bool: True if successful, False if owner already exists or error occurs.
        """
        if await self.is_owner_set():
            return False

        # Custom transaction for multi-table insert
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO system_config (key, value) VALUES ('owner_id', ?)",
                    (str(user_id),),
                )
                conn.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
            return True
        except sqlite3.Error as e:
            logger.error(f"Error setting bot owner: {e}")
            return False
        finally:
            conn.close()

    async def is_owner_set(self) -> bool:
        """
        Checks if a bot owner has been set.

        Returns:
            bool: True if an owner is set, False otherwise.
        """
        return await self.get_bot_owner() is not None

    # --- Product Management ---

    async def add_product(self, product_data: dict[str, Any]) -> Optional[str]:
        """
        Adds a new product to the inventory.

        Args:
            product_data (dict[str, Any]): Dictionary containing product fields.

        Returns:
            Optional[str]: The UUID of the new product, or None if failed.
        """
        # Ensure essential fields exist
        if not all(
            k in product_data
            for k in ["name", "description", "price", "quantity", "category"]
        ):
            logger.error(
                f"Missing essential product data for add_product: {product_data}"
            )
            return None

        product_id = str(uuid.uuid4())

        try:
            price_float = float(product_data.get("price", 0.0))
            price_cents = int(round(price_float * 100))
        except ValueError:
            logger.error(f"Invalid price format: {product_data.get('price')}")
            return None

        success = self._execute_write(
            """
            INSERT INTO products (
                id, name, description, price_cents, quantity, category, image_file_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_id,
                product_data.get("name"),
                product_data.get("description"),
                price_cents,
                product_data.get("quantity", 0),
                product_data.get("category"),
                product_data.get("image_file_id"),
            ),
        )
        return product_id if success else None

    async def get_product(self, product_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieves a specific product by its ID.

        Args:
            product_id (str): The product UUID.

        Returns:
            Optional[dict[str, Any]]: The product data, or None if not found.
        """
        row = self._execute_read_one(
            "SELECT * FROM products WHERE id = ? AND is_active = 1", (product_id,)
        )
        return self._row_to_product(row) if row else None

    async def get_all_products(self) -> List[dict[str, Any]]:
        """
        Retrieves all active products.

        Returns:
            List[dict[str, Any]]: A list of all active products.
        """
        rows = self._execute_read_all("SELECT * FROM products WHERE is_active = 1")
        return [self._row_to_product(row) for row in rows]

    async def get_products_by_category(
        self, category_name: str
    ) -> List[dict[str, Any]]:
        """
        Retrieves active products in a specific category.

        Args:
            category_name (str): The category name (case-insensitive search).

        Returns:
            List[dict[str, Any]]: A list of matching products.
        """
        rows = self._execute_read_all(
            "SELECT * FROM products WHERE category LIKE ? AND is_active = 1",
            (category_name,),
        )
        return [self._row_to_product(row) for row in rows]

    async def get_all_categories(self) -> List[str]:
        """
        Retrieves a list of unique categories.

        Returns:
            List[str]: A sorted list of category names.
        """
        rows = self._execute_read_all(
            "SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND is_active = 1 ORDER BY category"
        )
        return [row["category"] for row in rows]

    async def update_product(
        self, product_id: str, product_data: dict[str, Any]
    ) -> bool:
        """
        Updates an existing product.

        Args:
            product_id (str): The product UUID.
            product_data (dict[str, Any]): The fields to update.

        Returns:
            bool: False (Placeholder for Phase 2).
        """
        # TODO: Implement full update logic for Phase 2
        return False

    async def delete_product(self, product_id: str) -> bool:
        """
        Soft-deletes a product.

        Args:
            product_id (str): The product UUID.

        Returns:
            bool: True if successful, False otherwise.
        """
        return self._execute_write(
            "UPDATE products SET is_active = 0 WHERE id = ?", (product_id,)
        )

    async def update_product_stock(
        self, product_id: str, quantity_change: int
    ) -> Optional[int]:
        """
        Updates the stock quantity of a product atomically.

        Args:
            product_id (str): The product UUID.
            quantity_change (int): The amount to add (positive) or remove (negative).

        Returns:
            Optional[int]: The new quantity, or None if failed (e.g., negative stock).
        """
        conn = self._get_connection()
        try:
            with conn:  # Transaction start
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT quantity FROM products WHERE id = ?", (product_id,)
                )
                row = cursor.fetchone()

                if not row:
                    return None

                new_quantity = row["quantity"] + quantity_change
                if new_quantity < 0:
                    return None

                cursor.execute(
                    "UPDATE products SET quantity = ? WHERE id = ?",
                    (new_quantity, product_id),
                )
                # Transaction commits here automatically
                return new_quantity
        except sqlite3.Error as e:
            logger.error(f"Error updating stock: {e}")
            return None
        finally:
            conn.close()

    # --- Cart Management ---

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
        conn = self._get_connection()
        try:
            with conn:  # Transaction start
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO cart_items (user_id, product_id, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT (user_id, product_id) DO UPDATE SET
                        quantity = quantity + excluded.quantity
                    """,
                    (user_id, product_id, quantity),
                )
                cursor.execute(
                    "SELECT quantity FROM cart_items WHERE user_id = ? AND product_id = ?",
                    (user_id, product_id),
                )
                row = cursor.fetchone()
                if row:
                    return row["quantity"]
                else:
                    return None  # Should not happen
        except sqlite3.Error as e:
            logger.error(f"Error adding to cart: {e}")
            return None
        finally:
            conn.close()

    async def get_cart_items(self, user_id: int) -> dict[str, int]:
        """
        Retrieves the items in the user's cart.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict[str, int]: A dictionary mapping product IDs to quantities.
        """
        rows = self._execute_read_all(
            "SELECT product_id, quantity FROM cart_items WHERE user_id = ?",
            (user_id,),
        )
        return {row["product_id"]: row["quantity"] for row in rows}

    async def clear_cart(self, user_id: int) -> bool:
        """
        Clears all items from the user's cart.

        Args:
            user_id (int): The ID of the user.

        Returns:
            bool: True if the cart was successfully cleared, False otherwise.
        """
        return self._execute_write(
            "DELETE FROM cart_items WHERE user_id = ?", (user_id,)
        )

    # --- Order Management ---

    async def create_order(self, user_id: int) -> Optional[str]:
        """
        Creates an order from the user's current cart.

        Args:
            user_id (int): The ID of the user.

        Returns:
            Optional[str]: The order ID if successful, None if cart is empty.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Step A: Fetch Cart
            cursor.execute(
                """
                SELECT ci.product_id, ci.quantity, p.price_cents / 100.0 AS price
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.user_id = ?
                """,
                (user_id,),
            )
            cart_rows = cursor.fetchall()

            if not cart_rows:
                return None

            # Step B: Calculate Total
            total_amount = sum(row["quantity"] * row["price"] for row in cart_rows)

            # Step C: Create Order
            order_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO orders (id, user_id, total_amount, status)
                VALUES (?, ?, ?, 'completed')
                """,
                (order_id, user_id, total_amount),
            )

            # Step D: Move Items
            order_items_data = [
                (order_id, row["product_id"], row["quantity"], row["price"])
                for row in cart_rows
            ]
            cursor.executemany(
                """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                """,
                order_items_data,
            )

            # Step E: Cleanup
            cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))

        return order_id
