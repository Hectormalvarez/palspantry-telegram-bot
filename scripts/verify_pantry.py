#!/usr/bin/env python3
"""
Verification script for PalPantry Telegram Bot environment and API connectivity.
"""

import os
import sys
import sqlite3
import redis
from typing import Tuple

try:
    from dotenv import load_dotenv
    import requests
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install them with: pip install -r requirements-dev.txt")
    print(f"Import error: {e}")
    sys.exit(1)


def check_environment_variables() -> Tuple[bool, str]:
    """Check if BOT_TOKEN environment variable exists."""
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN')
    
    if bot_token:
        return True, "BOT_TOKEN found in environment"
    else:
        return False, "BOT_TOKEN not found in environment"


def check_telegram_api(bot_token: str) -> Tuple[bool, str]:
    """Check Telegram API connectivity using the bot token."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                username = data.get('result', {}).get('username', 'unknown')
                return True, f"Bot: @{username}"
            else:
                return False, f"API returned error: {data.get('description', 'Unknown error')}"
        else:
            return False, f"HTTP {response.status_code}: {response.reason}"
            
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def check_sqlite_database() -> Tuple[bool, str]:
    """Check SQLite database connectivity and structure."""
    try:
        db_path = 'pals_pantry.db'
        if not os.path.exists(db_path):
            return False, "Database file 'pals_pantry.db' not found"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for tables in the database
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        tables = cursor.fetchall()
        
        conn.close()
        
        if tables:
            table_count = len(tables)
            table_names = [table[0] for table in tables]
            return True, f"Found {table_count} tables: {', '.join(table_names)}"
        else:
            return False, "No tables found in database"
            
    except sqlite3.Error as e:
        return False, f"SQLite error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def check_redis_cache() -> Tuple[bool, str]:
    """Check Redis cache connectivity and basic operations."""
    try:
        load_dotenv()
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        # Create Redis connection
        r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # Test ping
        r.ping()
        
        # Test basic operations with a temporary key
        test_key = "healthcheck"
        test_value = "ok"
        
        # Set and get the test key
        r.set(test_key, test_value)
        retrieved_value = r.get(test_key)
        
        # Clean up the test key
        r.delete(test_key)
        
        if retrieved_value == test_value:
            return True, "Redis connection successful"
        else:
            return False, "Redis data integrity check failed"
            
    except redis.ConnectionError as e:
        return False, f"Redis connection failed: {str(e)}"
    except redis.TimeoutError as e:
        return False, f"Redis timeout: {str(e)}"
    except redis.AuthenticationError as e:
        return False, f"Redis authentication failed: {str(e)}"
    except Exception as e:
        return False, f"Redis error: {str(e)}"


def main():
    """Main verification function."""
    print("PalPantry Bot Verification")
    print("=" * 40)
    
    # Check 1: Environment Variables
    env_ok, env_msg = check_environment_variables()
    env_status = "PASS" if env_ok else "FAIL"
    print(f"[ENV] Environment Variables: {env_status}")
    if not env_ok:
        print(f"      {env_msg}")
    
    # Check 2: Telegram API Connection
    bot_token = os.getenv('BOT_TOKEN')
    if bot_token:
        tg_ok, tg_msg = check_telegram_api(bot_token)
        tg_status = "PASS" if tg_ok else "FAIL"
        print(f"[TG]  Telegram API Connection: {tg_status} ({tg_msg})")
        
        # Exit with code 1 if Telegram check fails
        if not tg_ok:
            sys.exit(1)
    else:
        print("[TG]  Telegram API Connection: FAIL (No BOT_TOKEN available)")
        sys.exit(1)
    
    # Check 3: SQLite Database
    db_ok, db_msg = check_sqlite_database()
    db_status = "PASS" if db_ok else "FAIL"
    print(f"[DB]  SQLite Database: {db_status} ({db_msg})")
    
    # Exit with code 1 if database check fails
    if not db_ok:
        sys.exit(1)
    
    # Check 4: Redis Cache
    redis_ok, redis_msg = check_redis_cache()
    redis_status = "PASS" if redis_ok else "FAIL"
    print(f"[REDIS] Redis Cache: {redis_status} ({redis_msg})")
    
    # Exit with code 1 if Redis check fails
    if not redis_ok:
        sys.exit(1)
    
    print("\nAll checks passed! ✅")


if __name__ == "__main__":
    main()