from django import forms

from .models import Product, Biller


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'kode_internal',
            'developer',
            'biller',
            'nominal',
            'price',
            'keterangan',
            'parse_text',
            'active'
        ]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['biller'].queryset = Biller.objects.filter(product__isnull=True)