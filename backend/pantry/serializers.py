from rest_framework import serializers
from .models import Product, CartItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'description']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.IntegerField(source='product.price_cents', read_only=True)

    class Meta:
        model = CartItem
        fields = ['product', 'product_name', 'quantity', 'price']
