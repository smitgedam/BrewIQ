from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .engine import (
    compute_pricing_suggestions,
    compute_demand_forecasts,
    compute_daily_waste_score,
    compute_revenue_trend,
    top_selling_items,
)
from .models import PricingSuggestion, DemandForecast
from apps.menu.models import MenuItem
from apps.accounts.decorators import role_required


@login_required
def intelligence_dashboard(request):
    """Main BrewIQ Intelligence dashboard."""
    suggestions = PricingSuggestion.objects.filter(
        status=PricingSuggestion.Status.PENDING
    ).select_related('menu_item').order_by('-confidence')[:10]

    forecasts = DemandForecast.objects.filter(
        forecast_date=timezone.now().date() + timezone.timedelta(days=1)
    ).select_related('menu_item').order_by('-predicted_quantity')[:10]

    waste_score   = compute_daily_waste_score()
    revenue_trend = compute_revenue_trend()
    top_items     = top_selling_items(days=7)

    return render(request, 'intelligence/dashboard.html', {
        'suggestions':   suggestions,
        'forecasts':     forecasts,
        'waste_score':   waste_score,
        'revenue_trend': revenue_trend,
        'top_items':     top_items,
    })


@login_required
@role_required('ADMIN', 'MANAGER')
def run_engine(request):
    """Manually trigger the intelligence engine (normally run by Celery nightly)."""
    if request.method != 'POST':
        return redirect('intelligence:dashboard')

    # ── Pricing suggestions ────────────────────────────────────────────────
    raw_suggestions = compute_pricing_suggestions()
    created_count = 0
    for s in raw_suggestions:
        try:
            item = MenuItem.objects.get(pk=s['item_id'])
        except MenuItem.DoesNotExist:
            continue
        # Avoid duplicate pending suggestions for the same item
        if not PricingSuggestion.objects.filter(
            menu_item=item, status=PricingSuggestion.Status.PENDING
        ).exists():
            PricingSuggestion.objects.create(
                menu_item=item,
                suggested_price=s['suggested_price'],
                reason=s['reason'],
                confidence=s['confidence'],
                peak_hour=s['peak_hour'],
                deviation_pct=s['deviation_pct'],
            )
            created_count += 1

    # ── Demand forecasts ───────────────────────────────────────────────────
    raw_forecasts = compute_demand_forecasts()
    for f in raw_forecasts:
        try:
            item = MenuItem.objects.get(pk=f['item_id'])
        except MenuItem.DoesNotExist:
            continue
        DemandForecast.objects.update_or_create(
            menu_item=item,
            forecast_date=f['forecast_date'],
            defaults={'predicted_quantity': f['predicted_quantity']},
        )

    messages.success(
        request,
        f'Engine run complete. {created_count} new pricing suggestion(s) generated. '
        f'{len(raw_forecasts)} demand forecast(s) updated.'
    )
    return redirect('intelligence:dashboard')


@login_required
@role_required('ADMIN', 'MANAGER')
def accept_suggestion(request, pk):
    suggestion = get_object_or_404(PricingSuggestion, pk=pk)
    if request.method == 'POST':
        suggestion.menu_item.current_price = suggestion.suggested_price
        suggestion.menu_item.save(update_fields=['current_price'])
        suggestion.status = PricingSuggestion.Status.ACCEPTED
        suggestion.actioned_at = timezone.now()
        suggestion.save()
        messages.success(
            request,
            f'Price for "{suggestion.menu_item.name}" updated to ₹{suggestion.suggested_price}.'
        )
    return redirect('intelligence:dashboard')


@login_required
@role_required('ADMIN', 'MANAGER')
def reject_suggestion(request, pk):
    suggestion = get_object_or_404(PricingSuggestion, pk=pk)
    if request.method == 'POST':
        suggestion.status = PricingSuggestion.Status.REJECTED
        suggestion.actioned_at = timezone.now()
        suggestion.save()
        messages.info(request, f'Suggestion for "{suggestion.menu_item.name}" rejected.')
    return redirect('intelligence:dashboard')


@login_required
def revenue_chart_data(request):
    """JSON endpoint for Chart.js revenue chart."""
    trend = compute_revenue_trend()
    return JsonResponse({
        'labels':   [d['date'] for d in trend],
        'revenues': [d['revenue'] for d in trend],
    })


@login_required
def top_items_data(request):
    """JSON endpoint for Chart.js top items chart."""
    items = top_selling_items(days=7, limit=5)
    return JsonResponse({
        'labels': [i['name'] for i in items],
        'values': [i['total_sold'] for i in items],
    })
