from django.contrib import admin
from .models import PricingSuggestion, DemandForecast


@admin.register(PricingSuggestion)
class PricingSuggestionAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'suggested_price', 'confidence', 'status', 'generated_at']
    list_filter  = ['status', 'generated_at']
    readonly_fields = ['generated_at', 'actioned_at']


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'forecast_date', 'predicted_quantity', 'generated_at']
    list_filter  = ['forecast_date']
    readonly_fields = ['generated_at']
