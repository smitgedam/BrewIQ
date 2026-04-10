from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from django.utils import timezone
import json

from .models import Order, OrderItem, CafeTable
from .forms import OrderCreateForm, TableForm
from apps.menu.models import MenuItem, Category
from apps.accounts.decorators import role_required


@login_required
def dashboard(request):
    today = timezone.now().date()
    orders_today = Order.objects.filter(created_at__date=today)
    active_orders = Order.objects.filter(
        status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY']
    ).select_related('table', 'created_by').prefetch_related('items')
    tables = CafeTable.objects.all()

    stats = {
        'total_orders_today': orders_today.count(),
        'revenue_today': orders_today.filter(status='COMPLETED').aggregate(
            total=Sum('items__unit_price'))['total'] or 0,
        'active_orders': active_orders.count(),
        'occupied_tables': tables.filter(is_occupied=True).count(),
    }
    return render(request, 'orders/dashboard.html', {
        'active_orders': active_orders,
        'tables': tables,
        'stats': stats,
    })


@login_required
def order_create(request):
    categories = Category.objects.prefetch_related('items').filter(is_active=True)
    form = OrderCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.created_by = request.user
        order.save()
        # Table is NOT marked occupied yet. We wait until items are confirmed
        # (order_add_items POST). This prevents ghost occupation if the user
        # abandons the add-items screen without submitting.
        messages.success(request, f'Order #{order.pk} created. Now add items.')
        return redirect('orders:order_add_items', pk=order.pk)
    return render(request, 'orders/order_create.html', {'form': form, 'categories': categories})


@login_required
def order_add_items(request, pk):
    order = get_object_or_404(Order, pk=pk)
    categories = Category.objects.prefetch_related('items').filter(
        is_active=True, items__is_available=True
    ).distinct()

    if request.method == 'POST':
        data = json.loads(request.body)
        items = data.get('items', [])
        # Clear existing pending items and re-add
        order.items.all().delete()
        for entry in items:
            menu_item = get_object_or_404(MenuItem, pk=entry['id'])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=entry['qty'],
                unit_price=menu_item.current_price,
                notes=entry.get('notes', ''),
            )
        order.status = Order.Status.CONFIRMED
        order.save()
        # NOW mark the table occupied — items are confirmed, order is real.
        if order.table:
            order.table.is_occupied = True
            order.table.save(update_fields=['is_occupied'])
        messages.success(request, 'Items added. Order confirmed!')
        return JsonResponse({'redirect': f'/orders/{order.pk}/'})

    return render(request, 'orders/order_add_items.html', {
        'order': order,
        'categories': categories,
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__menu_item').select_related('table', 'created_by'),
        pk=pk
    )
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_list(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('table', 'created_by').prefetch_related('items')
    if status_filter:
        orders = orders.filter(status=status_filter)
    orders = orders[:100]
    return render(request, 'orders/order_list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'statuses': Order.Status.choices,
    })


@login_required
@require_POST
def order_status_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    valid = [s[0] for s in Order.Status.choices]
    if new_status in valid:
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        # Free the table whenever the order reaches a terminal state —
        # COMPLETED (normal close) or CANCELLED (early abort).
        if new_status in ('COMPLETED', 'CANCELLED') and order.table:
            order.table.is_occupied = False
            order.table.save(update_fields=['is_occupied'])
        if request.htmx:
            return render(request, 'partials/_order_status_badge.html', {'order': order})
    return redirect('orders:order_detail', pk=pk)


@login_required
@require_POST
def cancel_order(request, pk):
    """
    Cancel a PENDING order that has no items confirmed yet.
    Safe to call from the add-items screen 'Cancel Order' button.
    Because the table is only marked occupied after confirmation,
    there is nothing to unset here for truly PENDING orders — but we
    handle the edge case of a CONFIRMED order being cancelled too,
    ensuring the table is always freed.
    """
    order = get_object_or_404(Order, pk=pk)
    if order.status not in (Order.Status.COMPLETED, Order.Status.CANCELLED):
        order.status = Order.Status.CANCELLED
        order.save(update_fields=['status', 'updated_at'])
        if order.table:
            order.table.is_occupied = False
            order.table.save(update_fields=['is_occupied'])
        messages.info(request, f'Order #{order.pk} has been cancelled.')
    return redirect('orders:dashboard')


@login_required
def kds_view(request):
    """Kitchen Display System — for chefs."""
    orders = Order.objects.filter(
        status__in=['CONFIRMED', 'PREPARING']
    ).prefetch_related('items__menu_item').select_related('table').order_by('created_at')
    return render(request, 'orders/kds.html', {'orders': orders})


@login_required
def kds_partial(request):
    """HTMX partial for KDS auto-refresh."""
    orders = Order.objects.filter(
        status__in=['CONFIRMED', 'PREPARING']
    ).prefetch_related('items__menu_item').select_related('table').order_by('created_at')
    return render(request, 'partials/_kds_list.html', {'orders': orders})


@login_required
@role_required('ADMIN', 'MANAGER')
def table_list(request):
    tables = CafeTable.objects.all()
    form = TableForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Table added.')
        return redirect('orders:table_list')
    return render(request, 'orders/table_list.html', {'tables': tables, 'form': form})


# ── Live-poll partial endpoints ───────────────────────────────────────────────

@login_required
def partial_dashboard_stats(request):
    """Stats row — orders today, revenue, active count, occupied tables."""
    today = timezone.now().date()
    orders_today = Order.objects.filter(created_at__date=today)
    tables = CafeTable.objects.all()
    stats = {
        'total_orders_today': orders_today.count(),
        'revenue_today': orders_today.filter(status='COMPLETED').aggregate(
            total=Sum('items__unit_price'))['total'] or 0,
        'active_orders': Order.objects.filter(
            status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY']).count(),
        'occupied_tables': tables.filter(is_occupied=True).count(),
    }
    return render(request, 'partials/_dashboard_stats.html', {'stats': stats})


@login_required
def partial_active_orders(request):
    """Active orders list on the dashboard."""
    active_orders = Order.objects.filter(
        status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY']
    ).select_related('table', 'created_by').prefetch_related('items').order_by('created_at')
    return render(request, 'partials/_active_orders.html', {'active_orders': active_orders})


@login_required
def partial_table_grid(request):
    """Table occupied/free grid."""
    tables = CafeTable.objects.all()
    return render(request, 'partials/_table_grid.html', {'tables': tables})


@login_required
def partial_order_detail(request, pk):
    """Full order detail card — status badge + action buttons + billing."""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__menu_item').select_related('table', 'created_by'),
        pk=pk
    )
    return render(request, 'partials/_order_detail_live.html', {'order': order})


@login_required
def partial_order_list(request):
    """Orders table body rows."""
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('table', 'created_by').prefetch_related('items')
    if status_filter:
        orders = orders.filter(status=status_filter)
    orders = orders[:100]
    return render(request, 'partials/_order_list_rows.html', {'orders': orders})
