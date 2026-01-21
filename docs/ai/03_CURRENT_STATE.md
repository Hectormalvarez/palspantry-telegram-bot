## 1. Active Milestone
**Version 0.2.7: Architecture & Maintenance**
* **Goal:** Prepare codebase for scale by decoupling text from logic (Centralized Message Registry).
* **Status:** In Progress
* **Current Task:** Create `tests/test_strings.py` and `resources/strings.py`.
* **Context:** The "Order Transaction Loop" (Milestone 2) is complete. We are pausing new features to refactor hardcoded strings into a centralized registry.

2. Recent Achievements

    (v0.2.0) Completed End-to-End Order Transaction Loop (Cart -> Checkout -> Database).

    (v0.2.0) Implemented Atomic Order Creation in SQLite.

    (v0.2.5) Implemented Persistent Home Dashboard logic.

    (v0.2.5) Updated /start to be state-aware (Shop vs Resume).
