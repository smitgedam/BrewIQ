from django.db import models
from apps.menu.models import MenuItem


class Ingredient(models.Model):
    class Unit(models.TextChoices):
        ML      = 'ml',     'Millilitres'
        LITRES  = 'litres', 'Litres'
        GRAMS   = 'grams',  'Grams'
        KG      = 'kg',     'Kilograms'
        PIECES  = 'pieces', 'Pieces'

    name             = models.CharField(max_length=200, unique=True)
    unit             = models.CharField(max_length=20, choices=Unit.choices)
    current_stock    = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cost_per_unit    = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"

    @property
    def is_low_stock(self):
        return self.current_stock <= self.low_stock_threshold

    @property
    def stock_status(self):
        if self.current_stock <= 0:
            return 'out'
        if self.is_low_stock:
            return 'low'
        return 'ok'


class MenuItemIngredient(models.Model):
    """How much of each ingredient is consumed per unit of a menu item."""
    menu_item      = models.ForeignKey(MenuItem, on_delete=models.CASCADE,
                                        related_name='ingredient_links')
    ingredient     = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                        related_name='menu_item_links')
    quantity_used  = models.DecimalField(max_digits=8, decimal_places=3)

    class Meta:
        unique_together = ('menu_item', 'ingredient')

    def __str__(self):
        return f"{self.menu_item.name} → {self.quantity_used} {self.ingredient.unit} {self.ingredient.name}"


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN     = 'IN',     'Stock In'
        OUT    = 'OUT',    'Stock Out'
        ADJUST = 'ADJUST', 'Adjustment'
        WASTE  = 'WASTE',  'Waste'

    ingredient    = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                       related_name='movements')
    movement_type = models.CharField(max_length=10, choices=MovementType.choices)
    quantity      = models.DecimalField(max_digits=10, decimal_places=3)
    notes         = models.CharField(max_length=300, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    created_by    = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.movement_type} {self.quantity} {self.ingredient.unit} of {self.ingredient.name}"
