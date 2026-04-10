from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from decimal import Decimal

from .models import Bill, GSTRate
from .utils import compute_bill
from apps.orders.models import Order


@login_required
def generate_bill(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)

    # Return existing bill if already generated
    if hasattr(order, 'bill'):
        return redirect('billing:bill_detail', pk=order.bill.pk)

    gst_rate = Decimal('5.00')
    try:
        default_gst = GSTRate.objects.get(is_default=True)
        gst_rate = default_gst.rate
    except GSTRate.DoesNotExist:
        pass

    computed = compute_bill(order, gst_rate)

    if request.method == 'POST':
        payment_mode = request.POST.get('payment_mode', 'Cash')
        bill = Bill.objects.create(
            order=order,
            payment_mode=payment_mode,
            is_paid=True,
            paid_at=timezone.now(),
            **computed,
        )
        order.status = Order.Status.COMPLETED
        order.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Bill generated. Total: ₹{bill.total_amount}')
        return redirect('billing:bill_detail', pk=bill.pk)

    return render(request, 'billing/generate_bill.html', {
        'order': order,
        **computed,
        'payment_modes': Bill._meta.get_field('payment_mode').choices,
    })


@login_required
def bill_detail(request, pk):
    bill = get_object_or_404(
        Bill.objects.select_related('order__table', 'order__created_by').prefetch_related(
            'order__items__menu_item'
        ),
        pk=pk
    )
    return render(request, 'billing/bill_detail.html', {'bill': bill})


@login_required
def bill_list(request):
    bills = Bill.objects.select_related('order').order_by('-generated_at')[:100]
    return render(request, 'billing/bill_list.html', {'bills': bills})


@login_required
def bill_print(request, pk):
    """Render a print-only receipt view."""
    bill = get_object_or_404(
        Bill.objects.select_related('order__table').prefetch_related('order__items__menu_item'),
        pk=pk
    )
    return render(request, 'billing/bill_print.html', {'bill': bill})


@login_required
def partial_bill_list(request):
    """Live billing history rows."""
    bills = Bill.objects.select_related('order').order_by('-generated_at')[:100]
    return render(request, 'partials/_bill_list_rows.html', {'bills': bills})
