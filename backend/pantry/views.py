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
