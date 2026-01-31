# 04_MVP_ROADMAP.md

## Scope: Version 1.0 (MVP) Launch - Distributed Service Architecture
This roadmap defines the critical path to a functional "Minimum Viable Product" using a distributed service model.
**Goal:** A complete, persistent E-commerce loop (Browse -> Order -> Fulfill) handled entirely within Telegram, with Django backend providing API services.

---

## Version 0.1: The Foundation (✅ Completed)
**Focus:** Reliability & Data Integrity.
* [x] **Test SQLite Persistence:** Verify schema creation, data types, and constraints.
* [x] **Migrate Bot:** Switch `bot_main.py` to use `SQLitePersistence` exclusively.
* [x] **Image Persistence:** Ensure file_ids for product images are stored/retrieved correctly.
* [x] **Cleanup:** Remove `InMemoryPersistence` to prevent technical debt.

## Version 0.2: The Customer Transaction Loop (✅ Completed)
**Focus:** Enabling the Customer to buy.
* [x] **Database:** Create `orders` and `order_items` tables.
* [x] **Persistence:** Implement `create_order` (Atomic Transaction).
* [x] **UI:** Wire 'Checkout' button to `create_order`.
* [x] **Customer UX:**
    * Send "Order Receipt" message to customer.
    * Clear the user's cart after successful order.
    * User Guidance (/start and Help handlers).
* [x] **Admin Alerts:** Trigger a Telegram message to the Owner ID when a new order is inserted.
* [x] **Polish:** Admin UI/UX Cleanup (Delete intermediate messages).

## Version 0.2.5: Navigation & State Refinement (✅ Completed)
**Focus:** Creating a persistent, state-aware user experience.
* [x] **Home Dashboard Logic:** Create a centralized `render_home_view(user_id)` function that checks cart status.
* [x] **Smart /start:** Update `/start` to use the Home Dashboard (showing "Resume Shopping" or "Checkout" if items exist).
* [x] **Loop Closure:** Update "Close Shop" button to edit the message back to the Home Dashboard instead of sending a "Closed" text.

## Version 0.2.7: Architecture & Maintenance (🚧 In Progress)
**Focus:** preparing the codebase for scale by decoupling text from logic.
* [ ] **Centralized Message Registry:** Create a `messages.py` or `resources/strings.py` to hold all static text.
* [ ] **Refactor Handlers:** Replace hardcoded strings in `handlers/` with references to the registry.

## Version 0.2.8: Database Parity & Schema Alignment (CRITICAL BLOCKER)
**Focus:** Align Django models with bot's SQLite schema to enable API integration.
**Status:** BLOCKING - Must complete before any Phase 2 work
**Impact:** Bot-to-Backend integration cannot proceed until models support:
- UUID primary keys for all entities (Products, Users, Orders, Carts)
- Integer cents pricing (replace DecimalField with IntegerField)
- Complete cart management models (Cart, CartItem)
- Order schema parity with bot's SQLite implementation
- Proper foreign key relationships and constraints

**Tasks:**
* [ ] **Model Schema Alignment:**
    * Update Product model: Add UUID primary key, change price to IntegerField (cents)
    * Update TelegramUser model: Add UUID primary key
    * Update Order model: Add UUID primary key, ensure schema matches bot implementation
    * Add Cart model: User relationship, created_at timestamp
    * Add CartItem model: Cart relationship, Product relationship, quantity field
* [ ] **Database Migration:**
    * Create Django migrations for all schema changes
    * Ensure backward compatibility where possible
    * Test migration on clean database
* [ ] **Schema Validation:**
    * Verify all field types match bot's SQLite schema exactly
    * Test model relationships and constraints
    * Validate UUID generation and handling

## Version 0.3: Infrastructure Parity (SERVICE PARITY FOCUS)
**Focus:** Ensure Django API achieves 100% feature parity with SQLitePersistence layer.
**Prerequisites:** Complete Version 0.2.8 (Database Parity)
**Status:** CRITICAL - Foundation for all subsequent API work
**Definition of Parity:** The Bot should not be able to tell the difference between the old SQLitePersistence and the new APIPersistence.

**Tasks:**
* [ ] **A: REST Endpoints (matching SQLite functionality):**
    * Implement complete CRUD operations for all entities (Products, Users, Orders, Carts, CartItems)
    * Ensure API responses match SQLitePersistence data structures exactly
    * Validate all edge cases and error conditions
* [ ] **B: Internal Secret Auth (shared key in .env):**
    * Implement simple API key authentication using shared secret
    * Add request/response validation middleware
* [ ] **C: Proper Error handling for 5xx/4xx API responses:**
    * Implement comprehensive error handling for API failures
    * Create graceful degradation when API is unavailable

## Version 0.4: Service Integration & Bot Migration (PLANNED)
**Focus:** Migrate bot from SQLite to Django API services.
**Prerequisites:** Complete Version 0.3 (Infrastructure Parity)
**Status:** BLOCKED until Infrastructure Parity is achieved

**Tasks:**
* [ ] **Bot API Client:**
    * Create API client wrapper for Django backend
    * Implement connection pooling and timeout handling
    * Add logging and monitoring for API calls
* [ ] **Persistence Migration:**
    * Update all bot handlers to use API client instead of SQLite
    * Maintain backward compatibility during transition
    * Validate data consistency between old and new systems
* [ ] **Service Health Monitoring:**
    * Add health check endpoints for Django services
    * Create alerting for service failures

## Version 0.5: The Owner Dashboard (PLANNED)
**Focus:** Enabling the Owner to fulfill orders through the distributed system.
**Prerequisites:** Complete Version 0.4 (Service Integration)
**Status:** BLOCKED until Service Integration is complete

**Tasks:**
* [ ] **Order Management API:**
    * Implement order status tracking through Django API
    * Add order filtering and search capabilities
    * Create order detail views with complete transaction history
* [ ] **Owner Dashboard Commands:**
    * `/orders`: List "Pending" orders via API (showing Order ID, Customer, Total)
    * `/order <id>`: View order details via API (Items, Quantities, Status)
    * `/fulfill <id>`: Update order status through API
* [ ] **Notifications:**
    * Send notifications to customers on status changes
    * Create audit trail for all order modifications

---

## Post-MVP (Out of Scope for v1.0)
* "Refactor: Centralized Message/String Management to decouple text from logic."
* "UX Refactor: Redesign 'Shop Closed' interaction (Move away from ephemeral status messages)."
* Real-time Payment Processing (Stripe/Telegram Payments).
* Customer Order History/Profiles.
* Web Dashboard.
* Advanced Analytics/Reporting.
