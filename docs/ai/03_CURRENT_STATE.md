## 1. Active Milestone
**Milestone 2: Database Persistence Hardening**
* **Goal:** Move from In-Memory storage to a robust SQLite implementation before adding more features.
* **Status:** `SQLitePersistence` class exists but is **untested**.

## 2. Current Task
**Task:** Implement Test Suite for SQLite Persistence.
* We need to verify that `persistence/sqlite_persistence.py` correctly implements `AbstractPantryPersistence`.
* We need to ensure data types (Currency/Float vs Int) round-trip correctly.

## 3. Known Issues / Blockers
* **Critical Gap:** `tests/test_persistence.py` currently tests `InMemoryPersistence`. We have zero coverage for `SQLitePersistence`.
* **Constraint:** We must use `pytest` with a temporary database file (fixtures), not the live `pals_pantry.db`.

## 4. Immediate Next Steps
1. Create `tests/persistence/test_sqlite_persistence.py`.
2. Run tests to verify Schema Creation and Data Integrity.
3. Once passed, delete `persistence/in_memory_persistence.py` (cleanup).