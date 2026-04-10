from django.db import models
from django.contrib.auth.models import User


class StaffProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        CASHIER = 'CASHIER', 'Cashier'
        CHEF = 'CHEF', 'Chef'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CASHIER)
    phone = models.CharField(max_length=15, blank=True)
    joined_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin_or_manager(self):
        return self.role in [self.Role.ADMIN, self.Role.MANAGER]
