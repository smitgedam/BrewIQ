from django import forms
from .models import Order, CafeTable


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_type', 'table', 'customer_name', 'notes']
        widgets = {
            'order_type': forms.Select(attrs={'class': 'form-input', 'id': 'order_type'}),
            'table': forms.Select(attrs={'class': 'form-input'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table'].queryset = CafeTable.objects.filter(is_occupied=False)
        self.fields['table'].required = False


class TableForm(forms.ModelForm):
    class Meta:
        model = CafeTable
        fields = ['number', 'capacity']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-input'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-input'}),
        }
