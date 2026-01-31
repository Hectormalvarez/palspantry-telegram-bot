import requests

BASE_URL = "http://web:8000/api"

def get_products():
    response = requests.get(f"{BASE_URL}/products/")
    response.raise_for_status()
    return response.json()