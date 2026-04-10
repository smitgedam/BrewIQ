"""
BrewIQ Intelligence Engine
==========================
Pure-Python analytical module using Pandas + NumPy.
No external ML library required.

Three capabilities:
  1. Dynamic pricing suggestions  — flag items with peak-hour demand spikes
  2. Demand forecasting           — predict next-day item quantities
  3. Waste / efficiency score     — daily score based on stock vs sales ratio
"""

import pandas as pd
import numpy as np
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta


# ── Thresholds (tune to taste) ───────────────────────────────────────────────
PEAK_DEVIATION_THRESHOLD = 0.25   # 25 % above hourly average → suggest price rise
MIN_DAYS_FOR_SUGGESTION  = 7      # need at least 7 days of data
PRICE_UPLIFT_FACTOR      = 0.40   # suggested uplift = deviation × this factor
FORECAST_WINDOW_DAYS     = 14     # rolling window for demand forecast


def _order_items_qs(days: int):
    """Return a base queryset of completed OrderItem records for the last N days."""
    from apps.orders.models import Order, OrderItem
    since = timezone.now() - timedelta(days=days)
    return (
        OrderItem.objects
        .filter(
            order__status=Order.Status.COMPLETED,
            order__created_at__gte=since,
        )
        .select_related('menu_item', 'order')
    )


# ── 1. Pricing Suggestions ────────────────────────────────────────────────────

def compute_pricing_suggestions() -> list[dict]:
    """
    For every active MenuItem, check whether demand at any hour-of-day
    exceeds the mean hourly demand by PEAK_DEVIATION_THRESHOLD.
    Returns a list of suggestion dicts (not yet saved to DB).
    """
    from apps.menu.models import MenuItem

    suggestions = []
    qs = _order_items_qs(days=30)
    if not qs.exists():
        return suggestions

    records = list(
        qs.values(
            'menu_item__id',
            'menu_item__name',
            'menu_item__base_price',
            'menu_item__current_price',
            'order__created_at',
            'quantity',
        )
    )
    df = pd.DataFrame(records)
    df.columns = ['item_id', 'item_name', 'base_price', 'current_price',
                   'created_at', 'quantity']
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['hour'] = df['created_at'].dt.hour
    df['date'] = df['created_at'].dt.date

    unique_days = df['date'].nunique()
    if unique_days < MIN_DAYS_FOR_SUGGESTION:
        return suggestions

    for item_id, group in df.groupby('item_id'):
        hourly = group.groupby('hour')['quantity'].sum()
        if hourly.empty or len(hourly) < 3:
            continue

        mean_demand = hourly.mean()
        if mean_demand == 0:
            continue

        peak_hour  = hourly.idxmax()
        peak_qty   = hourly.max()
        deviation  = (peak_qty - mean_demand) / mean_demand

        if deviation >= PEAK_DEVIATION_THRESHOLD:
            row         = group.iloc[0]
            base_price  = float(row['base_price'])
            uplift      = deviation * PRICE_UPLIFT_FACTOR
            suggested   = round(base_price * (1 + uplift), 2)
            confidence  = round(min(float(deviation), 1.0), 2)

            suggestions.append({
                'item_id':         int(item_id),
                'item_name':       row['item_name'],
                'current_price':   float(row['current_price']),
                'suggested_price': suggested,
                'peak_hour':       int(peak_hour),
                'deviation_pct':   round(float(deviation) * 100, 1),
                'confidence':      confidence,
                'reason': (
                    f"Demand at {int(peak_hour):02d}:00 is "
                    f"{round(deviation * 100, 1):.1f}% above daily average "
                    f"over the last {unique_days} days."
                ),
            })

    suggestions.sort(key=lambda x: x['confidence'], reverse=True)
    return suggestions


# ── 2. Demand Forecasting ─────────────────────────────────────────────────────

def compute_demand_forecasts() -> list[dict]:
    """
    For each active MenuItem, predict tomorrow's quantity using the
    rolling N-day average (same weekday weighting for accuracy).
    Returns a list of forecast dicts.
    """
    forecasts = []
    qs = _order_items_qs(days=FORECAST_WINDOW_DAYS)
    if not qs.exists():
        return forecasts

    records = list(
        qs.values('menu_item__id', 'menu_item__name', 'order__created_at', 'quantity')
    )
    df = pd.DataFrame(records, columns=['item_id', 'item_name', 'created_at', 'quantity'])
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['date']       = df['created_at'].dt.date
    df['weekday']    = df['created_at'].dt.weekday

    tomorrow         = (timezone.now() + timedelta(days=1)).date()
    tomorrow_weekday = tomorrow.weekday()

    for item_id, group in df.groupby('item_id'):
        daily = group.groupby('date')['quantity'].sum()
        if len(daily) < 3:
            continue

        # Weight: same-weekday occurrences get 2×, others 1×
        same_day = group[group['weekday'] == tomorrow_weekday].groupby('date')['quantity'].sum()
        if len(same_day) >= 2:
            predicted = int(round(same_day.mean() * 0.7 + daily.mean() * 0.3))
        else:
            predicted = int(round(daily.mean()))

        forecasts.append({
            'item_id':           int(item_id),
            'item_name':         group.iloc[0]['item_name'],
            'forecast_date':     tomorrow,
            'predicted_quantity': max(1, predicted),
        })

    return forecasts


# ── 3. Waste / Efficiency Score ───────────────────────────────────────────────

def compute_daily_waste_score() -> dict:
    """
    Waste score = (items_sold / items_theoretically_consumed) × 100
    Compares actual stock deductions against expected deductions from orders.
    Returns a dict with score (0–100) and breakdown.
    """
    from apps.inventory.models import StockMovement

    today = timezone.now().date()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    auto_out = StockMovement.objects.filter(
        movement_type=StockMovement.MovementType.OUT,
        notes__startswith='Auto-deducted',
        created_at__gte=today_start,
    ).aggregate(total=Sum('quantity'))['total'] or 0

    waste_out = StockMovement.objects.filter(
        movement_type=StockMovement.MovementType.WASTE,
        created_at__gte=today_start,
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total = float(auto_out) + float(waste_out)
    score = 100 if total == 0 else round((float(auto_out) / total) * 100, 1)

    return {
        'score':       score,
        'sold_units':  float(auto_out),
        'wasted_units': float(waste_out),
        'date':        today,
        'grade':       _score_grade(score),
    }


def _score_grade(score: float) -> str:
    if score >= 90:
        return 'Excellent'
    if score >= 75:
        return 'Good'
    if score >= 50:
        return 'Fair'
    return 'Needs Attention'


# ── 4. Revenue Trend (last 7 days) ───────────────────────────────────────────

def compute_revenue_trend() -> list[dict]:
    """Returns daily revenue for the past 7 completed days."""
    from apps.billing.models import Bill

    trend = []
    for i in range(6, -1, -1):
        day = (timezone.now() - timedelta(days=i)).date()
        total = Bill.objects.filter(
            generated_at__date=day,
            is_paid=True,
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        trend.append({'date': day.strftime('%d %b'), 'revenue': float(total)})
    return trend


# ── 5. Top Selling Items ──────────────────────────────────────────────────────

def top_selling_items(days: int = 7, limit: int = 5) -> list[dict]:
    """Returns top N items by quantity sold in the last N days."""
    qs = (
        _order_items_qs(days=days)
        .values('menu_item__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:limit]
    )
    return [{'name': r['menu_item__name'], 'total_sold': r['total_sold']} for r in qs]
