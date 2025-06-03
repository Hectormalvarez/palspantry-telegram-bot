# PalsPantry Telegram Bot

## Project Overview

PalsPantry is a Python-based Telegram bot designed to enable a single shop owner to manage an inventory of products and for customers to browse these products and place simple orders. The bot is built using the `python-telegram-bot` library and emphasizes a clean, abstracted persistence layer for future flexibility.

The initial MVP focuses on core product management for the shop owner and a browse-to-order-receipt flow for customers, without real-time payment processing.

## Core Features (MVP Focus)

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
    * (Future MVP) Edit existing products.
    * (Future MVP) Delete products.
    * (Future MVP) Quick stock updates (e.g., `/setstock <product_id> <quantity>`).
* **Order Management:**
    * Receive notifications for new customer orders.
    * Ability to view orders.
    * Ability to update order status (e.g., Pending, Preparing, Ready, Completed, Cancelled).

### For the Customer:
* **Browse Products:**
    * Start shopping via a command like `/shop` or `/menu`.
    * Browse products by categories.
    * View detailed information for each product (including image).
* **Shopping Cart:**
    * Add desired products to a temporary shopping cart (stored in user session data).
    * View the cart contents (`/cart`).
    * (Future MVP) Modify item quantities or remove items from the cart.
* **Place Order:**
    * "Checkout" the cart to place an order.
    * The bot generates an order receipt for the customer.
    * No real-time payment processing in MVP.
* **Order Status:**
    * (Future MVP) Customers can check the status of their orders.

## User Experience (UX) Flow Highlights

### Shop Owner UX:
1.  **Initial Setup:**
    * Run `/set_owner` to claim bot ownership.
2.  **Adding a Product (`/addproduct` - In Progress):**
    * A `ConversationHandler` guides the owner:
        * Bot: "What's the product's name?" -> User provides name.
        * Bot: "Now, a description?" -> User provides description.
        * Bot: "Price? (e.g., 10.99)" -> User provides price.
        * Bot: "Quantity available?" -> User provides quantity.
        * Bot: "Category? (Choose existing, type new, or skip)" -> User interacts.
        * Bot: "Optionally, send an image (or /skip)." -> User sends image or skips.
        * Bot: Shows a summary and asks for confirmation (`[Confirm & Add] [Edit] [Cancel]`).
3.  **Managing Products:**
    * Use `/myproducts` to see current inventory, with options to manage each item.
4.  **Handling Orders:**
    * Receives a message when a customer places an order.
    * Uses commands/inline keyboards to update the status of an order (e.g., `/updatestatus <order_id> <status>`).

### Customer UX:
1.  **Start Shopping:**
    * Customer sends `/shop` or `/menu`.
2.  **Navigation:**
    * Bot presents categories (e.g., via inline keyboards).
    * Customer selects a category to view products.
    * Products are listed (potentially with pagination for many items), each with a "View Details" option.
3.  **Product Interaction:**
    * Customer views full product details (name, description, price, image).
    * "Add to Cart" button available on product detail view.
4.  **Cart Management:**
    * Customer uses `/cart` to see items, total.
    * Options to modify cart (future MVP) or "Place Order".
5.  **Placing an Order:**
    * Customer confirms order from the cart.
    * Bot provides an "order receipt" message.
    * Bot informs the shop owner of the new order.

## Technical Stack & Key Components

* **Language:** Python 3
* **Core Library:** `python-telegram-bot` (v20+)
* **Configuration:** `config.py` loading from environment variables and `.env` files (using `python-dotenv`).
* **Logging:** Standard Python `logging` module, configured in `config.py`.
* **Persistence Abstraction Layer (PAL):**
    * `persistence/abstract_persistence.py`: Defines the interface for data operations.
    * `persistence/in_memory_persistence.py`: Current implementation. Stores bot owner and product data in memory. **Data resets on bot restart.**
* **Testing:**
    * `pytest` framework.
    * `pytest-asyncio` for async tests.
    * `pytest-mock` (and `unittest.mock`) for mocking.
    * Fixtures in `tests/conftest.py` for shared test setup.
* **Conversations:** `ConversationHandler` for multi-step interactions like adding products.
* **User Session Data:** `context.user_data` for temporary data like shopping carts.

## Current Development State & Workflow

This project is being developed iteratively.

1.  **Milestone 1: Robust Foundation & In-Memory Persistence (✅ COMPLETE)**
    * Project setup, basic bot connection.
    * Configuration management (`config.py`, `.env`).
    * Structured Logging.
    * Persistence Abstraction Layer (`AbstractPantryPersistence`).
    * `InMemoryPersistence` for bot owner.
    * `/set_owner` command implemented using PAL.
    * Unit tests for core setup, owner logic, and `InMemoryPersistence` (owner part).
    * Extended PAL & `InMemoryPersistence` for Product Management.
    * Unit tests for Product Management in `InMemoryPersistence`.

2.  **Milestone 2: Core Product & Shop Features (🚧 IN PROGRESS)**
    * **Current Focus:** Implementing the `/addproduct` `ConversationHandler` flow for the shop owner.
        * Initial step (collecting product name) is implemented.
    * **Next Steps:**
        * Complete all steps of the `/addproduct` conversation (description, price, quantity, category, image, confirmation).
        * Implement `/myproducts` command for the owner to view products.
        * Implement basic customer Browse flow (`/shop` -> categories -> product list -> product details).
        * Implement "Add to Cart" functionality (using `context.user_data`).
        * Implement `/cart` command.
        * Implement "Place Order" logic (generating receipts, notifying owner, updating stock).
        * Implement basic order status updates by the shop owner.


## Project Structure

```
palspantry-telegram-bot/
├── bot_main.py             # Main application logic, command handlers
├── config.py               # Configuration loading
├── persistence/
│   ├── __init__.py
│   ├── abstract_persistence.py # PAL interface
│   └── in_memory_persistence.py # In-memory data storage
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_bot_setup.py       # Tests for bot commands & setup
│   └── test_persistence.py     # Tests for persistence implementations
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment file (actual .env is gitignored)
├── .gitignore
└── pytest.ini              # Pytest configuration
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
    * Copy `.env.example` to `.env`.
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

## Future Considerations (Post-MVP)

* More robust persistence
* Cloud deployment (e.g., AWS Lambda with CDK).
* Advanced UX: Richer inline keyboard navigation, pagination for long lists.
* Telegram Payments integration.
* Notifications for stock running low.
* User accounts for customers (order history, preferences).
