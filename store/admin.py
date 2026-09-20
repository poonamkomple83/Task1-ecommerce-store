from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock")

    # ID aur Name par click karke product edit kar sakte hain
    list_display_links = ("id", "name")

    search_fields = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "city",
        "total_amount",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")

    search_fields = (
        "full_name",
        "email",
        "city",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
    )