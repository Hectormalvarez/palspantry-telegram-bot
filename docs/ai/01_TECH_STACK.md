# Technical Stack & Constraints

## 1. Core Stack
* **Language:** Python 3.12+
* **Framework:** `python-telegram-bot` (v20+) using `async`/`await`.
* **Database:** SQLite (using standard `sqlite3` library).
* **Configuration:** `python-dotenv` for secrets management.

## 2. Architectural Patterns
* **Persistence Layer:** MUST use the Repository Pattern.
    * All DB interactions happen in `persistence/`.
    * Handlers (`handlers/`) MUST NOT execute SQL queries directly.
    * Handlers receive data via the `AbstractPantryPersistence` interface.
* **State Management:**
    * Short-term UI state (e.g., conversation steps): `context.user_data`.
    * Long-term data (Carts, Orders, Inventory): MUST be persisted to SQLite.

## 3. Coding Standards
* **Formatting:** Follow `black` and `pylint` configurations present in the repo.
* **Type Hinting:** Required for all function signatures. Use `typing` module (e.g., `list[dict[str, Any]]`).
* **Docstrings:** Required for all handlers and persistence methods.
* **No ORMs:** Do not introduce SQLAlchemy or Django ORM. Write raw, parameterized SQL queries for simplicity and performance.

## 4. Testing
* **Framework:** `pytest` with `pytest-asyncio`.
* **Mocking:** Use `unittest.mock` to mock the Persistence Layer when testing Handlers.
