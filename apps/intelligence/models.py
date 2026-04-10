from django.db import models
from apps.menu.models import MenuItem


class PricingSuggestion(models.Model):
    class Status(models.TextChoices):
        PENDING  = 'PENDING',  'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'

    menu_item       = models.ForeignKey(MenuItem, on_delete=models.CASCADE,
                                         related_name='pricing_suggestions')
    suggested_price = models.DecimalField(max_digits=8, decimal_places=2)
    reason          = models.CharField(max_length=600)
    confidence      = models.FloatField(default=0.0)
    peak_hour       = models.PositiveSmallIntegerField(default=0)
    deviation_pct   = models.FloatField(default=0.0)
    status          = models.CharField(max_length=20, choices=Status.choices,
                                        default=Status.PENDING)
    generated_at    = models.DateTimeField(auto_now_add=True)
    actioned_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"Suggestion: {self.menu_item.name} → ₹{self.suggested_price} ({self.status})"


class DemandForecast(models.Model):
    menu_item          = models.ForeignKey(MenuItem, on_delete=models.CASCADE,
                                            related_name='forecasts')
    forecast_date      = models.DateField()
    predicted_quantity = models.PositiveIntegerField()
    generated_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-forecast_date', '-predicted_quantity']
        unique_together = ('menu_item', 'forecast_date')

    def __str__(self):
        return f"Forecast: {self.menu_item.name} — {self.predicted_quantity} on {self.forecast_date}"
