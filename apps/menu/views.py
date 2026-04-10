from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, MenuItem
from .forms import CategoryForm, MenuItemForm
from apps.accounts.decorators import role_required


@login_required
def menu_list(request):
    categories = Category.objects.prefetch_related('items').filter(is_active=True)
    all_categories = Category.objects.all()
    return render(request, 'menu/menu_list.html', {
        'categories': categories,
        'all_categories': all_categories,
    })


@login_required
@role_required('ADMIN', 'MANAGER')
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category created.')
        return redirect('menu:menu_list')
    return render(request, 'menu/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
@role_required('ADMIN', 'MANAGER')
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category updated.')
        return redirect('menu:menu_list')
    return render(request, 'menu/category_form.html', {'form': form, 'title': 'Edit Category'})


@login_required
@role_required('ADMIN', 'MANAGER')
def item_create(request):
    form = MenuItemForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        if not item.current_price:
            item.current_price = item.base_price
        item.save()
        messages.success(request, f'"{item.name}" added to menu.')
        return redirect('menu:menu_list')
    return render(request, 'menu/item_form.html', {'form': form, 'title': 'Add Menu Item'})


@login_required
@role_required('ADMIN', 'MANAGER')
def item_update(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    form = MenuItemForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'"{item.name}" updated.')
        return redirect('menu:menu_list')
    return render(request, 'menu/item_form.html', {'form': form, 'title': 'Edit Menu Item'})


@login_required
@role_required('ADMIN', 'MANAGER')
def item_toggle(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    item.is_available = not item.is_available
    item.save()
    status = 'available' if item.is_available else 'unavailable'
    messages.success(request, f'"{item.name}" marked as {status}.')
    return redirect('menu:menu_list')
