# 04_MVP_ROADMAP.md

## Scope: Version 1.0 (MVP) Launch
This roadmap defines the critical path to a functional "Minimum Viable Product."
**Goal:** A complete, persistent E-commerce loop (Browse -> Order -> Fulfill) handled entirely within Telegram.

---

## Phase 2: The Foundation (Current)
**Focus:** Reliability & Data Integrity.
* [ ] **Test SQLite Persistence:** Verify schema creation, data types, and constraints.
* [ ] **Migrate Bot:** Switch `bot_main.py` to use `SQLitePersistence` exclusively.
* [ ] **Image Persistence:** Ensure file_ids for product images are stored/retrieved correctly.
* [ ] **Cleanup:** Remove `InMemoryPersistence` to prevent technical debt.

## Phase 3: The Transaction Loop
**Focus:** Enabling the Customer to buy.
* [ ] **Database Schema Upgrade:**
    * Create `orders` table (UUID, user_id, status, timestamp).
    * Create `order_items` table (Snapshots of product name/price at time of purchase).
* [ ] **Checkout Logic:**
    * Implement "Place Order" button handler.
    * Validation: Check stock levels one last time before committing.
    * Atomic Transaction: Deduct stock + Create Order record.
* [ ] **Customer UX:**
    * Send "Order Receipt" message to customer.
    * Clear the user's cart after successful order.

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
* Real-time Payment Processing (Stripe/Telegram Payments).
* Customer Order History/Profiles.
* Web Dashboard.
* Advanced Analytics/Reporting.