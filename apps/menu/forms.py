from django import forms
from .models import Category, MenuItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'display_order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'display_order': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['category', 'name', 'description', 'base_price', 'current_price',
                  'is_available', 'is_vegetarian', 'prep_time_minutes', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'base_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'current_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'prep_time_minutes': forms.NumberInput(attrs={'class': 'form-input'}),
        }
