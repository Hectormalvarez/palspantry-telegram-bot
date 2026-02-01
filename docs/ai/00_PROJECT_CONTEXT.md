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
* **Persistence:** **SQLite (Fully Implemented)**.
* **Completed Features:**
    * Product Management (Add Product with Image).
    * Customer Navigation (Categories, Product Details, Back buttons).
    * Cart System (Add, View, Clear).
    * Checkout Logic (Creates Order, Clears Cart, Notifies Owner).
    * Persistent Home Dashboard (/start awareness).
* **Missing Features:**
    * **Centralized String Registry (Hardcoded strings currently in handlers).**
    * Owner Dashboard (Ability to list/manage orders via command).
    * Order History for customers.
* **Transition Status:** Beginning migration to Decoupled Django/Docker Architecture (Phase 0: Infrastructure & Diagnostic Tooling).
* **API Integration Progress:** Successfully implemented `APIPersistence` class with verified JSON-to-dictionary transformation for cart management, establishing foundation for Django API integration.

## 4. Target Architecture
**Decoupled Django/Docker Architecture:**
* **Bot Service:** Telegram bot as a separate service communicating with Django API.
* **Django Backend:** Django 5.x REST API for business logic and data management.
* **PostgreSQL 16:** Primary database for production data storage.
* **Redis 7:** Caching layer and session management.
* **Docker:** Containerization for consistent development and deployment environments.
* **Service Communication:** RESTful API calls between Bot and Django services.

## 4. AI Interaction Protocol (The "Context System")
This project uses a strict context management system to ensure continuity across chat sessions.

### The "Context Triad"
1. **Static Context (`00_PROJECT_CONTEXT.md`, `01_TECH_STACK.md`, `02_DATA_SCHEMA.md`):**
    * These files define the *Rules*, *Architecture*, and *Constraints*.
    * **Rule:** These rarely change. If they conflict with your training data, these files win.

2. **Dynamic Context (`03_CURRENT_STATE.md`):**
    * This file defines the *Now*.
    * **Rule:** This file is the single source of truth for "What are we working on?". You MUST read this first to orient yourself.
    * **Rule:** If the user asks "What's next?", look here.

3. **The Codebase:**
    * The implementation details.

### Interaction Rules
* **No External Data:** Do not use information about the user from outside this repo's context.
* **Update State:** If a major task is completed during a session, the AI should suggest updating `03_CURRENT_STATE.md` to reflect the new reality.
