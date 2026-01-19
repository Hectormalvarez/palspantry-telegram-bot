# 04_MVP_ROADMAP.md

## Scope: Version 1.0 (MVP) Launch
This roadmap defines the critical path to a functional "Minimum Viable Product."
**Goal:** A complete, persistent E-commerce loop (Browse -> Order -> Fulfill) handled entirely within Telegram.

---

## Phase 2: The Foundation
**Focus:** Reliability & Data Integrity.
* [x] **Test SQLite Persistence:** Verify schema creation, data types, and constraints.
* [x] **Migrate Bot:** Switch `bot_main.py` to use `SQLitePersistence` exclusively.
* [x] **Image Persistence:** Ensure file_ids for product images are stored/retrieved correctly.
* [x] **Cleanup:** Remove `InMemoryPersistence` to prevent technical debt.

## Milestone 4: The Transaction Loop
**Focus:** Enabling the Customer to buy.
* [x] Database: Create `orders` and `order_items` tables
* [x] Persistence: Implement `create_order` (Atomic Transaction)
* [x] UI: Wire 'Checkout' button to `create_order`
* [x] **Customer UX:**
    * Send "Order Receipt" message to customer.
    * Clear the user's cart after successful order.

## Milestone 4.5: MVP Polish
* [x] User Guidance (/start and Help handlers).
* [ ] Enhanced Order Receipts (User summary).
* [x] Admin Notifications (Notify owner on purchase).
* [ ] UI/UX Cleanup (Delete intermediate admin messages).

## Phase 4: The Owner Dashboard
**Focus:** Enabling the Owner to fulfill.
* [ ] **Notifications:** Trigger a Telegram message to the Owner ID when a new order is inserted.
* [ ] **Order Management Commands:**
    * `/orders`: List "Pending" orders.
    * `/order <id>`: View details of a specific order.
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
