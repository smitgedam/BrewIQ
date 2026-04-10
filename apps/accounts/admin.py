from django.contrib import admin
from .models import StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'joined_date', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
