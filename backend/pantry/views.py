from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Product, CartItem, TelegramUser
from .serializers import ProductSerializer, CartItemSerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CartViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing cart items for a specific user.
    """
    def list(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter items by the Telegram ID
        queryset = CartItem.objects.filter(user__telegram_id=user_id)
        serializer = CartItemSerializer(queryset, many=True)
        
        # Return wrapped in 'items' key to match test expectation
        return Response({'items': serializer.data})
    
    def create(self, request):
        """
        Add an item to the cart.
        """
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        
        if not all([user_id, product_id, quantity]):
            return Response(
                {"error": "user_id, product_id, and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = TelegramUser.objects.get(telegram_id=user_id)
            product = Product.objects.get(id=product_id)
        except (TelegramUser.DoesNotExist, Product.DoesNotExist):
            return Response(
                {"error": "Invalid user_id or product_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # If item exists, update the quantity
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({'items': [serializer.data]}, status=status_code)
