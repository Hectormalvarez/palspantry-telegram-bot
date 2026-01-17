# Project Context: PalsPantry Bot

## 1. Project Overview
PalsPantry is a Python-based Telegram bot designed to be a lightweight e-commerce solution for a **single shop owner**. It allows the owner to manage a simple inventory and customers to browse, cart, and order items.

## 2. Core Personas
* **The Shop Owner (Admin):**
    * Single user (identified by Telegram ID).
    * Capabilities: Add/Edit/Delete products, Update stock, View incoming orders, Change order status.
    * *Constraint:* There is no web dashboard. All management happens via Telegram commands.
* **The Customer:**
    * Any Telegram user interacting with the bot.
    * Capabilities: Browse categories, View product details (with images), Add to cart, Checkout.

## 3. Current Implementation Status
* **Architecture:** Modular handler structure, Abstract Persistence Layer.
* **Persistence:** Currently migrating from In-Memory (volatile) to SQLite.
* **Missing Features:**
    * Product Images (Code exists but is skipped in handlers).
    * Checkout Logic (Cart exists, but "Place Order" does nothing).
    * Order History.
