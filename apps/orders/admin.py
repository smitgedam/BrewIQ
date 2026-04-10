from django.contrib import admin
from .models import CafeTable, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'order_type', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'order_type', 'created_at']
    inlines = [OrderItemInline]


@admin.register(CafeTable)
class CafeTableAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity', 'is_occupied']
    list_editable = ['is_occupied']
