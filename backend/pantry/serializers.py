from rest_framework import serializers
from .models import Product, CartItem

class ProductSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(source='price_cents', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'description']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
