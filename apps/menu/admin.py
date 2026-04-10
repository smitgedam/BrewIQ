from django.contrib import admin
from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'current_price', 'is_available', 'is_vegetarian']
    list_filter = ['category', 'is_available', 'is_vegetarian']
    search_fields = ['name']
    list_editable = ['is_available', 'current_price']
