from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ingredient, StockMovement, MenuItemIngredient
from .forms import IngredientForm, StockMovementForm, MenuItemIngredientForm
from apps.accounts.decorators import role_required


@login_required
def inventory_dashboard(request):
    ingredients = Ingredient.objects.all()
    low_stock = [i for i in ingredients if i.is_low_stock]
    recent_movements = StockMovement.objects.select_related('ingredient').order_by('-created_at')[:20]
    return render(request, 'inventory/dashboard.html', {
        'ingredients': ingredients,
        'low_stock': low_stock,
        'recent_movements': recent_movements,
    })


@login_required
@role_required('ADMIN', 'MANAGER')
def ingredient_create(request):
    form = IngredientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ingredient added.')
        return redirect('inventory:dashboard')
    return render(request, 'inventory/ingredient_form.html', {'form': form, 'title': 'Add Ingredient'})


@login_required
@role_required('ADMIN', 'MANAGER')
def ingredient_update(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    form = IngredientForm(request.POST or None, instance=ingredient)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ingredient updated.')
        return redirect('inventory:dashboard')
    return render(request, 'inventory/ingredient_form.html', {'form': form, 'title': 'Edit Ingredient'})


@login_required
@role_required('ADMIN', 'MANAGER')
def stock_movement_create(request):
    form = StockMovementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        movement = form.save(commit=False)
        movement.created_by = request.user.get_full_name() or request.user.username
        ingredient = movement.ingredient
        if movement.movement_type == StockMovement.MovementType.IN:
            ingredient.current_stock += movement.quantity
        elif movement.movement_type in [StockMovement.MovementType.OUT,
                                         StockMovement.MovementType.WASTE]:
            ingredient.current_stock = max(0, ingredient.current_stock - movement.quantity)
        else:  # ADJUST
            ingredient.current_stock = movement.quantity
        ingredient.save(update_fields=['current_stock'])
        movement.save()
        messages.success(request, f'Stock movement recorded for {ingredient.name}.')
        return redirect('inventory:dashboard')
    return render(request, 'inventory/movement_form.html', {'form': form})


@login_required
@role_required('ADMIN', 'MANAGER')
def link_ingredient(request):
    form = MenuItemIngredientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ingredient linked to menu item.')
        return redirect('inventory:dashboard')
    links = MenuItemIngredient.objects.select_related('menu_item', 'ingredient').all()
    return render(request, 'inventory/link_form.html', {'form': form, 'links': links})


@login_required
def partial_inventory_levels(request):
    """Live stock levels + low-stock alert banner."""
    ingredients = Ingredient.objects.all()
    low_stock = [i for i in ingredients if i.is_low_stock]
    recent_movements = StockMovement.objects.select_related('ingredient').order_by('-created_at')[:20]
    return render(request, 'partials/_inventory_levels.html', {
        'ingredients': ingredients,
        'low_stock': low_stock,
        'recent_movements': recent_movements,
    })
