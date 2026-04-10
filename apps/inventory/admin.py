from django.contrib import admin
from .models import Ingredient, MenuItemIngredient, StockMovement


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'current_stock', 'low_stock_threshold', 'stock_status']
    list_filter = ['unit']
    search_fields = ['name']

    def stock_status(self, obj):
        return obj.stock_status
    stock_status.short_description = 'Status'


@admin.register(MenuItemIngredient)
class MenuItemIngredientAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'ingredient', 'quantity_used']
    list_filter = ['menu_item__category']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['ingredient', 'movement_type', 'quantity', 'created_by', 'created_at']
    list_filter = ['movement_type', 'created_at']
    readonly_fields = ['created_at']
