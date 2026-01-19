# 04_MVP_ROADMAP.md

## Scope: Version 1.0 (MVP) Launch
This roadmap defines the critical path to a functional "Minimum Viable Product."
**Goal:** A complete, persistent E-commerce loop (Browse -> Order -> Fulfill) handled entirely within Telegram.

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

## Version 0.3: The Owner Dashboard (🚧 In Progress)
**Focus:** Enabling the Owner to fulfill.
* [ ] **Order List Command:**
    * `/orders`: List "Pending" orders (showing Order ID, Customer, Total).
* [ ] **Order Detail Command:**
    * `/order <id>`: View details of a specific order (Items, Quantities).
* [ ] **Status Workflow:**
    * Add controls to change order status: `Pending` -> `Ready` -> `Completed`.
    * Notify Customer on status change.

---

## Post-MVP (Out of Scope for v1.0)
* "Refactor: Centralized Message/String Management to decouple text from logic."
* "UX Refactor: Redesign 'Shop Closed' interaction (Move away from ephemeral status messages)."
* Real-time Payment Processing (Stripe/Telegram Payments).
* Customer Order History/Profiles.
* Web Dashboard.
* Advanced Analytics/Reporting.