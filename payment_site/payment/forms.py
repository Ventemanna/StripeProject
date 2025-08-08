from django import forms
from django.core.validators import MinValueValidator


class ItemForm(forms.Form):
    quantity = forms.IntegerField(min_value=0)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            return forms.ValidationError("Quantity must be greater than 0")
        return quantity