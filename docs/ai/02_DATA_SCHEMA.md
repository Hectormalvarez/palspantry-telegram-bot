# Database Schema & Data Models

## 1. Design Decisions
* **Currency:** `orders` and `order_items` currently use REAL (floats) for totals, while `products` uses INTEGER (cents).
* **IDs:**
    * `products`, `orders`: UUID Strings.
    * `users`: Telegram User ID (Integer).
* **Boolean:** Stored as `INTEGER` (0 or 1) per SQLite standards.

## 2. Tables

### `system_config`
*Global bot settings.*
| Column | Type | Notes |
| :--- | :--- | :--- |
| `key` | TEXT PRIMARY KEY | e.g., 'owner_id' |
| `value` | TEXT | |

### `users`
*Tracks customers and the owner.*
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | INTEGER PRIMARY KEY | The Telegram User ID |
| `username` | TEXT | |
| `first_name` | TEXT | |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### `products`
*The inventory catalog.*
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | TEXT PRIMARY KEY | UUID |
| `name` | TEXT | NOT NULL |
| `description` | TEXT | |
| `price_cents` | INTEGER | NOT NULL |
| `quantity` | INTEGER | NOT NULL (Current Stock) |
| `category` | TEXT | |
| `image_file_id` | TEXT | Telegram File ID |
| `is_active` | INTEGER | 1 = Visible, 0 = Soft Deleted |

### `cart_items`
*Persistent shopping carts.*
| Column | Type | Notes |
| :--- | :--- | :--- |
| `user_id` | INTEGER | FK -> users.id |
| `product_id` | TEXT | FK -> products.id |
| `quantity` | INTEGER | > 0 |
| **Constraint** | UNIQUE(user_id, product_id) | Prevent duplicate rows |

### `orders`
*Completed transactions.*
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | TEXT PRIMARY KEY | UUID |
| `user_id` | INTEGER | FK -> users.id |
| `total_amount` | REAL | Snapshot of total cost (Float) |
| `status` | TEXT | 'completed' (Default) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### `order_items`
*Line items for orders (Snapshot of product state at time of purchase).*
| Column | Type | Notes |
| :--- | :--- | :--- |
| `order_id` | TEXT | FK -> orders.id |
| `product_id` | TEXT | FK -> products.id |
| `quantity` | INTEGER | |
| `unit_price` | REAL | Price at moment of purchase (Float) |
