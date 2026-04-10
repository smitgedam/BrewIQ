from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import LoginForm, StaffCreateForm, StaffUpdateForm
from .models import StaffProfile
from .decorators import role_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('orders:dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next', 'orders:dashboard'))
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
@role_required('ADMIN', 'MANAGER')
def staff_list(request):
    staff = StaffProfile.objects.select_related('user').all().order_by('role')
    return render(request, 'accounts/staff_list.html', {'staff': staff})


@login_required
@role_required('ADMIN')
def staff_create(request):
    form = StaffCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Staff member created successfully.')
        return redirect('accounts:staff_list')
    return render(request, 'accounts/staff_form.html', {'form': form, 'title': 'Add Staff'})


@login_required
@role_required('ADMIN')
def staff_update(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)
    initial = {
        'first_name': profile.user.first_name,
        'last_name': profile.user.last_name,
        'email': profile.user.email,
    }
    form = StaffUpdateForm(request.POST or None, instance=profile, initial=initial)
    if request.method == 'POST' and form.is_valid():
        profile = form.save()
        profile.user.first_name = form.cleaned_data['first_name']
        profile.user.last_name = form.cleaned_data['last_name']
        profile.user.email = form.cleaned_data['email']
        profile.user.save()
        messages.success(request, 'Staff member updated.')
        return redirect('accounts:staff_list')
    return render(request, 'accounts/staff_form.html', {'form': form, 'title': 'Edit Staff'})
