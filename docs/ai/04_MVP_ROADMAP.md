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

## Version 0.2.5: Navigation & State Refinement (✅ Completed)
**Focus:** Creating a persistent, state-aware user experience.
* [x] **Home Dashboard Logic:** Create a centralized `render_home_view(user_id)` function that checks cart status.
* [x] **Smart /start:** Update `/start` to use the Home Dashboard (showing "Resume Shopping" or "Checkout" if items exist).
* [x] **Loop Closure:** Update "Close Shop" button to edit the message back to the Home Dashboard instead of sending a "Closed" text.

## Version 0.2.7: Architecture & Maintenance (🚧 In Progress)
**Focus:** preparing the codebase for scale by decoupling text from logic.
* [ ] **Centralized Message Registry:** Create a `messages.py` or `resources/strings.py` to hold all static text.
* [ ] **Refactor Handlers:** Replace hardcoded strings in `handlers/` with references to the registry.

## Version 0.3: The Owner Dashboard (Planned)
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
