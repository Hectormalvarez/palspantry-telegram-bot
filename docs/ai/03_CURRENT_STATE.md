## 1. Active Milestone
**Phase 2: Service Integration**
* **Goal:** Integrate Django backend with Telegram bot and implement decoupled service architecture.
* **Status:** In Progress
* **Context:** Moving from isolated services to integrated system with proper API communication.

## 2. Recent Achievements
* **(Phase 0)** Completed Infrastructure Verification Utility: All checks (ENV, TG, DB, REDIS, PG) are PASSING in Docker.
* **(Phase 1)** Dockerized the base environment: Bot, Postgres, and Redis services are online and networked.
* **(v0.2.7)** Completed v0.2.7: Full Message Registry & Architecture Refactor.
* **(v0.2.5)** Implemented Persistent Home Dashboard logic in `handlers/general/start.py` and `shop.py`.
* **(v0.2.5)** Updated "Close Shop" to navigate back to Dashboard instead of sending ephemeral messages.
* **(v0.2.0)** Implemented Atomic Order Creation in SQLite (`create_order`).
* **(v0.2.0)** Implemented Checkout flow: Cart -> Order -> Receipt -> Owner Notification.
* **(v0.3.0)** Refactored `bot_main.py` to use Domain-Based Handler Registration (Scalable Architecture).
* **(C2.2)** Initial API Setup: Created basic Django REST API endpoints for Products and Orders (Commits: 0fe5919/dda9005).
* **(C2.1)** Initial Model Registration: Basic Django models created but require schema alignment (Commit: c4a1b36).

## 3. Current Development State
### Phase 0: Infrastructure & Diagnostic Tooling
- [x] **C0.1:** Environment Setup & Telegram Bot Configuration
- [x] **C0.2:** SQLite Database Integration & Schema Definition
- [x] **C0.3:** Redis Integration for Caching & Session Management
- [x] **C0.4:** PostgreSQL Database Setup & Migration Strategy

### Phase 1: Dockerization & Service Orchestration
- [x] **C1.1:** Create Dockerfile for Python bot environment
- [x] **C1.2:** Configure docker-compose.yaml with bot, postgres, redis services
- [x] **C1.3:** Set up environment variables and secrets management
- [x] **C1.4:** Implement health checks and service dependencies

### Phase 1.5: Clean Architecture Refactor (Service Isolation)
- [x] **C1.5.1:** Create dedicated bot directory structure
- [x] **C1.5.2:** Fix import paths and module references
- [x] **C1.5.3:** Update Docker configuration for new structure

### Phase 2: Service Integration (Distributed Architecture)
- [ ] **C2.1:** Align Django Models with Schema (Integer Cents & Cart Models) **[BLOCKING - NEEDS REWORK]**
  - *Current models (c4a1b36) require complete schema realignment*
  - Must support UUID primary keys, IntegerField for cents, and cart management
- [ ] **C2.2:** Implement Complete REST API Endpoints for all entities
  - *Basic endpoints created (0fe5919/dda9005) but need expansion*
- [ ] **C2.3:** Update Bot to Use Django API instead of SQLite
- [ ] **C2.4:** Add Authentication and Error Handling for API calls
- [ ] **C2.5:** Implement Redis Caching for API responses
- [ ] **C2.6:** Add Service Health Checks and Monitoring

## 4. Blocking Issues
### Database Schema Mismatch (CRITICAL BLOCKER)
**Issue:** Django models in `backend/pantry/models.py` do not match the required schema for Phase 2 integration.
**Impact:** Bot-to-Backend integration is BLOCKED until models support:
- UUID primary keys for all entities
- Integer cents pricing (not DecimalField)
- Complete cart management models
- Order schema parity with bot's SQLite implementation
**Status:** High priority - must be resolved before any API integration work
