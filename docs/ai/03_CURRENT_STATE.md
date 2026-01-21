## 1. Active Milestone
**Version 0.2.7: Architecture & Maintenance**
* **Goal:** Prepare codebase for scale by decoupling text from logic (Centralized Message Registry).
* **Status:** In Progress
* **Current Task:** 1. Create `resources/strings.py`. 2. Create `tests/test_strings.py`. 3. Refactor Handlers to use the registry.
* **Context:** The "Order Transaction Loop" (Milestone 2) and "Home Dashboard" (Milestone 2.5) are complete. New features are paused until strings are centralized.

2. Recent Achievements
    (v0.2.5) Implemented Persistent Home Dashboard logic in `handlers/general/start.py` and `shop.py`.
    (v0.2.5) Updated "Close Shop" to navigate back to Dashboard instead of sending ephemeral messages.
    (v0.2.0) Implemented Atomic Order Creation in SQLite (`create_order`).
    (v0.2.0) Implemented Checkout flow: Cart -> Order -> Receipt -> Owner Notification.
