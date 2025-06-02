import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "No BOT_TOKEN found in environment variables. Please set it in your .env file or environment."
    )


# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging():
    """Sets up basic logging."""
    logging.basicConfig(
        level=LOG_LEVEL, format=LOG_FORMAT, handlers=[logging.StreamHandler()]
    )

setup_logging()
