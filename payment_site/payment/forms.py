from django import forms

class ItemForm(forms.Form):
    quantity = forms.IntegerField()

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            return forms.ValidationError("Quantity must be greater than 0")
        return quantity