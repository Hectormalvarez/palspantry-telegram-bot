import requests
from .abstract_persistence import AbstractPantryPersistence

class APIPersistence(AbstractPantryPersistence):
    def __init__(self, base_url: str, api_key: str = "test-key"):
        self.base_url = base_url
        self.api_key = api_key

    def _get_headers(self):
        return {'X-API-KEY': self.api_key}

    async def get_cart_items(self, user_id: int) -> dict[str, int]:
        response = requests.get(
            f"{self.base_url}/api/cart/", 
            params={'user_id': user_id}, 
            headers=self._get_headers()
        )
        data = response.json()
        items = data.get('items', [])
        return {item['product']['id']: item['quantity'] for item in items}

    async def add_to_cart(self, user_id: int, product_id: str, quantity: int):
        pass

    async def remove_from_cart(self, user_id: int, product_id: str, quantity: int):
        pass

    async def clear_cart(self, user_id: int):
        pass

    async def get_cart_total(self, user_id: int) -> float:
        pass

    async def create_order(self, user_id: int, items: dict[str, int]) -> int:
        pass

    async def get_order(self, order_id: int) -> dict:
        pass

    async def update_order_status(self, order_id: int, status: str):
        pass

    async def get_user_orders(self, user_id: int) -> list[dict]:
        pass

    async def get_bot_owner(self):
        return None

    async def set_bot_owner(self, user_id):
        return False

    async def is_owner_set(self):
        return False

    async def add_product(self, product_data):
        return None

    async def get_product(self, product_id):
        return None

    async def get_all_products(self):
        return []

    async def get_products_by_category(self, cat):
        return []

    async def get_all_categories(self):
        return []

    async def update_product(self, pid, data):
        return False

    async def delete_product(self, pid):
        return False

    async def update_product_stock(self, pid, change):
        return None
