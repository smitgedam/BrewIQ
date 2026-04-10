from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import Order
from .models import StockMovement


@receiver(post_save, sender=Order)
def deduct_inventory_on_completion(sender, instance, **kwargs):
    """
    When an order reaches COMPLETED status, deduct ingredients
    from stock and record a StockMovement for each deduction.
    Only fires when status field is updated to COMPLETED.
    """
    update_fields = kwargs.get('update_fields')
    # Only act when status is explicitly saved
    if update_fields and 'status' not in update_fields:
        return
    if instance.status != Order.Status.COMPLETED:
        return

    for order_item in instance.items.select_related('menu_item').prefetch_related(
        'menu_item__ingredient_links__ingredient'
    ):
        for link in order_item.menu_item.ingredient_links.all():
            deduction = link.quantity_used * order_item.quantity
            ingredient = link.ingredient
            ingredient.current_stock = max(0, ingredient.current_stock - deduction)
            ingredient.save(update_fields=['current_stock'])

            StockMovement.objects.create(
                ingredient=ingredient,
                movement_type=StockMovement.MovementType.OUT,
                quantity=deduction,
                notes=f"Auto-deducted for Order #{instance.pk}",
                created_by='system',
            )
