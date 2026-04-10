from django import forms
from .models import Ingredient, MenuItemIngredient, StockMovement


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'unit', 'current_stock', 'low_stock_threshold', 'cost_per_unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'unit': forms.Select(attrs={'class': 'form-input'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
            'cost_per_unit': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['ingredient', 'movement_type', 'quantity', 'notes']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-input'}),
            'movement_type': forms.Select(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
            'notes': forms.TextInput(attrs={'class': 'form-input'}),
        }


class MenuItemIngredientForm(forms.ModelForm):
    class Meta:
        model = MenuItemIngredient
        fields = ['menu_item', 'ingredient', 'quantity_used']
        widgets = {
            'menu_item': forms.Select(attrs={'class': 'form-input'}),
            'ingredient': forms.Select(attrs={'class': 'form-input'}),
            'quantity_used': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
        }
