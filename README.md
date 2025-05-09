# PalsPantry Telegram Bot

## Project Overview

This project is a Python-based Telegram bot designed for PalsPantry. It utilizes the `python-telegram-bot` library to interact with the Telegram Bot API.

The initial core functionality allows for the designation of a single "bot owner" through the `/set_owner` command. The first user to issue this command will be registered as the owner.

## Key Components

-   **`bot_main.py`**: The main script containing the bot's logic, including command handlers and application setup.
-   **`requirements.txt`**: Lists project dependencies, primarily `python-telegram-bot`, `pytest`, `pytest-asyncio`, and `pytest-mock`.
-   **`tests/test_bot_setup.py`**: Contains unit tests (using `pytest`) to verify bot initialization and the owner assignment feature.

## Getting Started

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set Bot Token**:
    Export your Telegram bot token as an environment variable:
    ```bash
    export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    ```
3.  **Run the Bot**:
    ```bash
    python bot_main.py
    ```
4.  **Run Tests**:
    ```bash
    pytest
    ```

This project serves as a foundational piece for potentially more complex pantry management features in the future.
