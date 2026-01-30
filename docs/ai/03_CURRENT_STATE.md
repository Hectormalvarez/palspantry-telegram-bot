## 1. Active Milestone
**Phase 0: Infrastructure & Diagnostic Tooling**
* **Goal:** Establish foundation for decoupled Django/Docker architecture.
* **Status:** In Progress
* **Context:** Preparing migration from monolithic Telegram bot to service-based architecture with Django API backend.

## 2. Recent Achievements
* **(v0.2.7)** Completed v0.2.7: Full Message Registry & Architecture Refactor.
* **(v0.2.5)** Implemented Persistent Home Dashboard logic in `handlers/general/start.py` and `shop.py`.
* **(v0.2.5)** Updated "Close Shop" to navigate back to Dashboard instead of sending ephemeral messages.
* **(v0.2.0)** Implemented Atomic Order Creation in SQLite (`create_order`).
* **(v0.2.0)** Implemented Checkout flow: Cart -> Order -> Receipt -> Owner Notification.
* **(v0.3.0)** Refactored `bot_main.py` to use Domain-Based Handler Registration (Scalable Architecture).

## 3. Phase 0 Granular Commits
* **C0.1:** Environment Setup & Telegram Bot Configuration
* **C0.2:** SQLite Database Integration & Schema Definition
* **C0.3:** Redis Integration for Caching & Session Management
* **C0.4:** PostgreSQL Database Setup & Migration Strategy
