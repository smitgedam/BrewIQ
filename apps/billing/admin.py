from django.contrib import admin
from .models import Bill, GSTRate


@admin.register(GSTRate)
class GSTRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'is_default']
    list_editable = ['is_default']


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'subtotal', 'gst_amount', 'total_amount',
                    'payment_mode', 'is_paid', 'generated_at']
    list_filter = ['payment_mode', 'is_paid', 'generated_at']
    readonly_fields = ['generated_at', 'paid_at']
