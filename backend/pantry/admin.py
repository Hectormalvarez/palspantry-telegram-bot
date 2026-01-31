from django.contrib import admin
from .models import Product, TelegramUser, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_cents', 'stock', 'created_at')
    search_fields = ('name',)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'first_name', 'created_at')
    search_fields = ('telegram_id', 'username')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
