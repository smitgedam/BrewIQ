from django.db import models
from apps.orders.models import Order


class GSTRate(models.Model):
    name       = models.CharField(max_length=100)
    rate       = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 5.00 for 5%
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.rate}%)"

    def save(self, *args, **kwargs):
        if self.is_default:
            GSTRate.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Bill(models.Model):
    order         = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='bill')
    subtotal      = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate      = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    gst_amount    = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount  = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode  = models.CharField(max_length=50, default='Cash',
                                      choices=[('Cash','Cash'),('Card','Card'),('UPI','UPI')])
    is_paid       = models.BooleanField(default=False)
    generated_at  = models.DateTimeField(auto_now_add=True)
    paid_at       = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Bill #{self.pk} for Order #{self.order.pk} — ₹{self.total_amount}"
