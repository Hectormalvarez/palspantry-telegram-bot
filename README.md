# PalsPantry Telegram Bot

## Project Overview

PalsPantry is a Python-based Telegram bot designed to enable a single shop owner to manage an inventory of products and for customers to browse these products and place simple orders. The bot is built using the `python-telegram-bot` library and emphasizes a clean, abstracted persistence layer for future flexibility.

The current implementation includes full product management, customer browsing with cart and checkout, order creation with owner notifications, and a persistent home dashboard.

## Core Features

### General

* `/help`: View a list of available commands.
* `/start`: Persistent home dashboard aware of cart status.

### For the Shop Owner (Bot Owner):
* **Bot Ownership:** Securely designate a single bot owner via the `/set_owner` command (first user to issue becomes owner).
* **Product Management:**
    * `/addproduct`: A multi-step conversation to add new products with details:
        * Name
        * Description
        * Price
        * Stock Quantity
        * Category
        * Image (optional)
    * `/myproducts`: View a list of all added products.
* **Order Notifications:** Automatic Telegram messages when customers place orders.

### For the Customer:
* **Browse Products:**
    * Start shopping via `/start` dashboard or `/shop`.
    * Browse products by categories with navigation buttons.
    * View detailed information for each product (including image).
* **Shopping Cart:**
    * Add products to cart.
    * View cart contents and total.
    * Clear cart.
* **Checkout & Orders:**
    * Checkout creates order in database.
    * Receive order receipt.
    * Cart clears after order.
    * Order stored with snapshot of product data.

## User Experience (UX) Flow Highlights

### Shop Owner UX:
1.  **Initial Setup:**
    * Run `/set_owner` to claim bot ownership.
2.  **Adding a Product (`/addproduct`):**
    * A `ConversationHandler` guides the owner:
        * Bot: "What's the product's name?" -> User provides name.
        * Bot: "Now, a description?" -> User provides description.
        * Bot: "Price? (e.g., 10.99)" -> User provides price.
        * Bot: "Quantity available?" -> User provides quantity.
        * Bot: "Category? (Choose existing, type new, or skip)" -> User interacts.
        * Bot: "Optionally, send an image (or /skip)." -> User sends image or skips.
        * Bot: Shows a summary and asks for confirmation (`[Confirm & Add] [Edit] [Cancel]`).
3.  **Managing Products:**
    * Use `/myproducts` to see current inventory.
4.  **Handling Orders:**
    * Receives automatic notification when a customer places an order.

### Customer UX:
1.  **Home Dashboard:**
    * `/start` shows dashboard: "Shop" or "Resume Shopping" if cart has items.
2.  **Navigation:**
    * Select category to view products.
    * Products listed with "View Details" buttons.
3.  **Product Interaction:**
    * View full details (name, description, price, image).
    * "Add to Cart" button.
4.  **Cart Management:**
    * `/cart` shows items, total, "Checkout" or "Clear Cart".
5.  **Placing an Order:**
    * Checkout creates order, clears cart, sends receipt.
    * Owner notified of new order.

## Technical Stack & Key Components

* **Language:** Python 3
* **Core Library:** `python-telegram-bot` (v20+)
* **Configuration:** `config.py` loading from environment variables and `.env` files (using `python-dotenv`).
* **Logging:** Standard Python `logging` module, configured in `config.py`.
* **Persistence Abstraction Layer (PAL):**
    * `persistence/abstract_persistence.py`: Defines the interface for data operations.
    * `persistence/in_memory_persistence.py`: Deprecated implementation (replaced by SQLite).
    * `persistence/sqlite_persistence.py`: Current active implementation using SQLite for persistent data storage.
* **Testing:**
    * `pytest` framework.
    * `pytest-asyncio` for async tests.
    * `pytest-mock` (and `unittest.mock`) for mocking.
    * Fixtures in `tests/conftest.py` for shared test setup.
* **Conversations:** `ConversationHandler` for multi-step interactions like adding products.
* **User Session Data:** `context.user_data` for temporary data like shopping carts.

## Current Development State & Workflow

This project is being developed iteratively with versioned milestones.

### Version 0.1: The Foundation (✅ Completed)
* Project setup, configuration, logging.
* Persistence Abstraction Layer (PAL).
* SQLite migration from in-memory.
* Bot owner management.
* Product management with images.

### Version 0.2: The Customer Transaction Loop (✅ Completed)
* Customer navigation (categories, product details, back buttons).
* Cart system (add, view, clear).
* Checkout logic (creates order, clears cart, notifies owner).

### Version 0.2.5: Navigation & State Refinement (✅ Completed)
* Persistent home dashboard (/start awareness).
* Updated "Close Shop" to navigate back to dashboard.

### Version 0.2.7: Architecture & Maintenance (🚧 In Progress)
* Centralized Message Registry to decouple text from logic.
* Refactor handlers to use the registry.


## Project Structure

```
palspantry-telegram-bot/
├── bot_main.py             # Main application logic and command handlers
├── config.py               # Configuration loading from environment
├── handlers/               # Modular handler structure
│   ├── customer/
│   │   ├── cart.py         # Cart management (add, view, clear)
│   │   └── shop.py         # Product browsing and navigation
│   ├── general/
│   │   ├── start.py        # Persistent home dashboard
│   │   ├── help.py         # Help command
│   │   └── unknown.py      # Unknown command handler
│   ├── owner/
│   │   └── set_owner.py    # Bot ownership setup
│   └── product/
│       └── add_product.py  # Product addition with conversation
├── persistence/            # Persistence Abstraction Layer
│   ├── abstract_persistence.py # PAL interface
│   ├── sqlite_persistence.py   # SQLite implementation
│   └── in_memory_persistence.py # Deprecated in-memory implementation
├── tests/                  # Comprehensive test suite
│   ├── conftest.py         # Shared test fixtures
│   ├── test_bot_setup.py   # Bot initialization tests
│   ├── handlers/
│   │   ├── customer/
│   │   ├── general/
│   │   └── product/
│   └── persistence/
├── docs/                   # AI context and documentation
│   └── ai/
│       ├── 00_PROJECT_CONTEXT.md
│       ├── 01_TECH_STACK.md
│       ├── 02_DATA_SCHEMA.md
│       ├── 03_CURRENT_STATE.md
│       └── 04_MVP_ROADMAP.md
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml          # Project configuration
├── pytest.ini              # Pytest configuration
├── .pylintrc               # Linting configuration
├── .env.sample             # Environment variables template
├── .gitignore
└── README.md
```

## Getting Started (Local Development)

1.  **Clone the repository.**
2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up your Bot Token:**
    * Copy `.env.sample` to `.env`.
    * Edit `.env` and add your Telegram Bot token:
        ```
        BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
        ```
5.  **Run the bot:**
    ```bash
    python bot_main.py
    ```
6.  **Run tests:**
    ```bash
    pytest
    ```

## Future Considerations

### Immediate Next Steps (Version 0.2.7+)
* **Centralized String Registry:** Create `resources/strings.py` to hold all hardcoded text, decoupling messages from logic.
* **Owner Dashboard:** Implement commands for owners to list and manage orders (`/orders`, `/order <id>`).
* **Customer Order History:** Allow customers to view their past orders.

### Post-MVP Enhancements
* Real-time payment processing (Stripe/Telegram Payments).
* Web dashboard for owners.
* Advanced analytics and reporting.
* Customer profiles and preferences.
* Cloud deployment options.
