import sqlite3
import os
import pytest
from unittest import mock
import sys

# Add project root to sys.path to allow importing 'database'
# This assumes tests are run from the project root or that the 'tests' directory is a module
# A more robust solution might involve a conftest.py or adjusting PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database import create_tables, get_db_connection, add_or_update_user, DATABASE_NAME as ACTUAL_DATABASE_NAME

TEST_DATABASE_NAME = 'test_palspantry.db'

@pytest.fixture(scope="function")
def setup_test_database():
    """
    Fixture to set up and tear down a test database for each test function.
    It patches the DATABASE_NAME in the database module to use a test-specific DB.
    """
    # Ensure no previous test database file exists
    if os.path.exists(TEST_DATABASE_NAME):
        os.remove(TEST_DATABASE_NAME)

    # Patch the database name within the 'database' module for the duration of the test
    with mock.patch('database.DATABASE_NAME', TEST_DATABASE_NAME):
        yield # Test runs here
    
    # Teardown: remove the test database file after the test
    if os.path.exists(TEST_DATABASE_NAME):
        os.remove(TEST_DATABASE_NAME)

def test_create_tables_initializes_all_tables(setup_test_database):
    """
    Tests if create_tables function correctly creates all necessary tables.
    """
    # Call the function that creates tables (uses the patched TEST_DATABASE_NAME)
    create_tables()

    # Connect to the test database to verify
    conn = None
    try:
        # get_db_connection will use the patched TEST_DATABASE_NAME
        conn = get_db_connection() 
        cursor = conn.cursor()

        # Check if tables exist
        tables_to_check = ['User', 'Product', 'Order', 'OrderItem']
        for table_name in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            result = cursor.fetchone()
            assert result is not None, f"Table '{table_name}' was not created."
            assert result[0] == table_name, f"Table '{table_name}' name mismatch."
        
        # Optionally, check for specific columns (example for User table)
        cursor.execute("PRAGMA table_info(User)")
        columns = [row[1] for row in cursor.fetchall()]
        assert 'telegram_id' in columns
        assert 'name' in columns

        cursor.execute("PRAGMA table_info(Product)")
        columns = [row[1] for row in cursor.fetchall()]
        assert 'id' in columns
        assert 'name' in columns
        assert 'price' in columns
        assert 'category' in columns
        
        cursor.execute("PRAGMA table_info('Order')") # Note: 'Order' is quoted
        columns = [row[1] for row in cursor.fetchall()]
        assert 'id' in columns
        assert 'user_telegram_id' in columns
        assert 'order_date' in columns
        assert 'total_price' in columns
        assert 'status' in columns

        cursor.execute("PRAGMA table_info(OrderItem)")
        columns = [row[1] for row in cursor.fetchall()]
        assert 'id' in columns
        assert 'order_id' in columns
        assert 'product_id' in columns
        assert 'quantity' in columns
        assert 'price_at_order' in columns

    finally:
        if conn:
            conn.close()

def test_get_db_connection_uses_correct_database(setup_test_database):
    """
    Tests if get_db_connection connects to the (patched) test database.
    """
    # This will create and connect to TEST_DATABASE_NAME due to the fixture's patch
    conn = get_db_connection()
    assert conn is not None
    # Check the database file path if possible (can be tricky with sqlite3)
    # For now, just ensure it creates the test DB file
    conn.close() # Close connection to allow file check
    assert os.path.exists(TEST_DATABASE_NAME), "Test database file was not created by get_db_connection."

def test_add_new_user(setup_test_database):
    """Tests adding a new user to the User table."""
    create_tables() # Ensure tables are created in the test DB
    
    telegram_id = 12345
    name = "Test User"
    add_or_update_user(telegram_id, name)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, name FROM User WHERE telegram_id = ?", (telegram_id,))
    user_record = cursor.fetchone()
    conn.close()

    assert user_record is not None, "User was not added to the database."
    assert user_record['telegram_id'] == telegram_id
    assert user_record['name'] == name

def test_add_existing_user_does_not_duplicate_or_error(setup_test_database):
    """Tests that attempting to add an existing user does not create a duplicate or raise an error."""
    create_tables()

    telegram_id = 67890
    name = "Existing User"
    
    # Add user for the first time
    add_or_update_user(telegram_id, name)
    
    # Attempt to add the same user again
    add_or_update_user(telegram_id, name) # Should be ignored by INSERT OR IGNORE

    # Attempt to add the same user with a different name (current logic ignores, doesn't update name)
    add_or_update_user(telegram_id, "New Name For Existing User")


    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM User WHERE telegram_id = ?", (telegram_id,))
    count = cursor.fetchone()[0]
    
    cursor.execute("SELECT name FROM User WHERE telegram_id = ?", (telegram_id,))
    user_name_record = cursor.fetchone()['name']
    conn.close()

    assert count == 1, "User was duplicated or an error occurred."
    assert user_name_record == name, "User's name was updated, but current logic should ignore."


def test_add_or_update_user_different_users(setup_test_database):
    """Tests adding multiple different users."""
    create_tables()

    user1_id = 111
    user1_name = "User One"
    add_or_update_user(user1_id, user1_name)

    user2_id = 222
    user2_name = "User Two"
    add_or_update_user(user2_id, user2_name)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM User WHERE telegram_id = ?", (user1_id,))
    record1 = cursor.fetchone()
    cursor.execute("SELECT name FROM User WHERE telegram_id = ?", (user2_id,))
    record2 = cursor.fetchone()
    
    conn.close()

    assert record1 is not None and record1['name'] == user1_name
    assert record2 is not None and record2['name'] == user2_name
