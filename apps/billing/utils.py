from decimal import Decimal, ROUND_HALF_UP


def compute_bill(order, gst_rate_percent: Decimal) -> dict:
    """
    Compute billing amounts for an order.
    All arithmetic uses Decimal to avoid floating-point errors.
    Returns a dict ready to create a Bill instance.
    """
    subtotal = sum(item.subtotal for item in order.items.all())
    subtotal = Decimal(str(subtotal))
    gst_rate = Decimal(str(gst_rate_percent))

    gst_amount = (subtotal * gst_rate / 100).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    total_amount = (subtotal + gst_amount).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    return {
        'subtotal': subtotal,
        'gst_rate': gst_rate,
        'gst_amount': gst_amount,
        'total_amount': total_amount,
    }
