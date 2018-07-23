from django import forms
from django.db.models import Q, F

from .models import Transaksi, Product, Biller


# class TransaksiModelForm(forms.ModelForm):
#     class Meta:
#         model = Transaksi
#         fields = ['product', 'phone']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['operator','kode_internal', 'nominal', 'price','biller', 'kode_external', 'keterangan', 'parse_text', 'active']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['biller'].queryset = Biller.objects.filter(product__isnull=True)

class TransaksiForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['trx_code','price','phone','status','user','pembukuan','catatan_modal']
