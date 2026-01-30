#!/usr/bin/env python3
"""
Verification script for PalPantry Telegram Bot environment and API connectivity.
"""

import os
import sys
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
    
    print("\nAll checks passed! ✅")


if __name__ == "__main__":
    main()