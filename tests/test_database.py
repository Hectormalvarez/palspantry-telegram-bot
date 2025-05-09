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

from database import create_tables, get_db_connection, DATABASE_NAME as ACTUAL_DATABASE_NAME

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
