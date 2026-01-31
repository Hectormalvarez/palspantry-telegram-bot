# Technical Stack & Constraints

## 1. Core Stack
* **Language:** Python 3.12+
* **Framework:** `python-telegram-bot` (v20+) using `async`/`await`.
* **Database:** SQLite (using standard `sqlite3` library).
* **Configuration:** `python-dotenv` for secrets management.
* **Target Stack (Phase 0+):**
    * **Django 5.x:** REST API backend for business logic
    * **PostgreSQL 16:** Primary production database
    * **Redis 7:** Caching API responses and handling session state
    * **Docker:** Containerization for consistent environments

## 2. Architectural Patterns
* **Current Architecture:** Monolithic Telegram bot with abstract persistence layer.
    * **Persistence Layer:** MUST use the Repository Pattern.
        * All DB interactions happen in `persistence/`.
        * Handlers (`handlers/`) MUST NOT execute SQL queries directly.
        * Handlers receive data via the `AbstractPantryPersistence` interface.
    * **State Management:**
        * Short-term UI state (e.g., conversation steps): `context.user_data`.
        * Long-term data (Carts, Orders, Inventory): MUST be persisted to SQLite.

* **Target Architecture (Phase 0+):** Decoupled Service-Based Model
    * **Bot Service:** Telegram bot as independent service
    * **Django API Service:** RESTful backend for business logic
    * **Database Service:** PostgreSQL for persistent storage
    * **Cache Service:** Redis for performance optimization
    * **Service Communication:** HTTP REST API calls between services
    * **Container Orchestration:** Docker Compose for local development

## 3. Coding Standards
* **Formatting:** Follow `black` and `pylint` configurations present in the repo.
* **Type Hinting:** Required for all function signatures. Use `typing` module (e.g., `list[dict[str, Any]]`).
* **No ORMs:** Do not introduce SQLAlchemy or Django ORM. Write raw, parameterized SQL queries for simplicity and performance.
* **Context Hygiene:**
    * `docs/ai/03_CURRENT_STATE.md` MUST be updated at the end of every significant feature or session.
    * Do not leave the state as "Working on X" if X was completed.

## 4. Documentation & Comments
* **Docstring Style:** MUST use **Google Style** docstrings for all functions and classes.
    * Must include `Args:`, `Returns:`, and `Raises:` (if applicable) sections.
* **Module Headers:** Every Python file must start with a docstring block describing the module's responsibility.
* **Inline Comments:** Use sparingly. Explain *why* a complex logic block exists, not *what* the code is doing.
* **TODOs:** Format as `# TODO: Description of task`.

### Example Docstring:
```python
def calculate_total(price: int, quantity: int) -> int:
    """
    Calculates the total price in cents.

    Args:
        price (int): The unit price in cents.
        quantity (int): The number of items.

    Returns:
        int: The total cost.
    """
    return price * quantity
```

##  5. Testing

    Framework: pytest with pytest-asyncio.

    Mocking: Use unittest.mock to mock the Persistence Layer when testing Handlers.

## 6. String Management (v0.2.7+)
* **Pattern:** Centralized Nested Classes.
* **File:** `resources/strings.py`
* **Structure:**
  - `class Strings`: Root class.
  - Nested classes (e.g., `class Cart`) for grouping static text.
  - Static methods for messages requiring dynamic variables (e.g., formatting names/prices).
* **Rule:** Do not hardcode user-facing text in handlers. Import from `resources.strings`.
