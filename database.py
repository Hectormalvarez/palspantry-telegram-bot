import sqlite3
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DATABASE_NAME = 'palspantry.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def create_tables():
    """Creates the necessary tables in the database if they don't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # User table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                telegram_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        logger.info("User table created or already exists.")

        # Product table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Product (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL,
                category TEXT
            )
        ''')
        logger.info("Product table created or already exists.")

        # Order table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "Order" (  -- Quoted "Order" as it's a keyword
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_telegram_id INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_price REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending', -- e.g., pending, confirmed, shipped, delivered, cancelled
                FOREIGN KEY (user_telegram_id) REFERENCES User (telegram_id)
            )
        ''')
        logger.info("Order table created or already exists.")

        # OrderItem table (junction table for Order and Product)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS OrderItem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_at_order REAL NOT NULL, -- Price of the product at the time of order
                FOREIGN KEY (order_id) REFERENCES "Order" (id),
                FOREIGN KEY (product_id) REFERENCES Product (id)
            )
        ''')
        logger.info("OrderItem table created or already exists.")

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error during table creation: {e}")
    finally:
        conn.close()

def add_or_update_user(telegram_id: int, name: str):
    """Adds a new user or updates the name if the user already exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Using INSERT OR IGNORE to only insert if the telegram_id doesn't exist.
        # If you wanted to update the name if it changed, you might use
        # INSERT INTO User (telegram_id, name) VALUES (?, ?)
        # ON CONFLICT(telegram_id) DO UPDATE SET name=excluded.name;
        # For now, just inserting if new is sufficient.
        cursor.execute('''
            INSERT OR IGNORE INTO User (telegram_id, name)
            VALUES (?, ?)
        ''', (telegram_id, name))
        conn.commit()
        if cursor.rowcount > 0:
            logger.info(f"User {name} (ID: {telegram_id}) added to the database.")
        else:
            logger.info(f"User {name} (ID: {telegram_id}) already exists in the database.")
    except sqlite3.Error as e:
        logger.error(f"Database error when adding/updating user {telegram_id}: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # This allows running `python database.py` to initialize the database.
    logger.info(f"Initializing database '{DATABASE_NAME}'...")
    create_tables()
    logger.info("Database initialization complete.")
