from django.db import models
from django.conf import settings
from apps.menu.models import MenuItem


class CafeTable(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    capacity = models.PositiveSmallIntegerField(default=4)
    is_occupied = models.BooleanField(default=False)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Table {self.number}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'PENDING',   'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        PREPARING = 'PREPARING', 'Preparing'
        READY     = 'READY',     'Ready'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class OrderType(models.TextChoices):
        DINE_IN  = 'DINE_IN',  'Dine In'
        TAKEAWAY = 'TAKEAWAY', 'Takeaway'

    table = models.ForeignKey(CafeTable, null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='orders')
    order_type = models.CharField(max_length=10, choices=OrderType.choices,
                                   default=OrderType.DINE_IN)
    status = models.CharField(max_length=20, choices=Status.choices,
                               default=Status.PENDING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.PROTECT,
                                    related_name='created_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    customer_name = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        table_info = f"Table {self.table.number}" if self.table else "Takeaway"
        return f"Order #{self.pk} - {table_info} ({self.status})"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def status_color(self):
        colors = {
            'PENDING':   'yellow',
            'CONFIRMED': 'blue',
            'PREPARING': 'orange',
            'READY':     'green',
            'COMPLETED': 'gray',
            'CANCELLED': 'red',
        }
        return colors.get(self.status, 'gray')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
