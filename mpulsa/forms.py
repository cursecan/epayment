from django import forms

from .models import Transaksi, Product


class TransaksiModelForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['product', 'phone']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['kode_internal' ,'operator','type_layanan', 'nominal', 'price', 'kode_external', 'price_beli', 'keterangan', 'parse_text']

class TransaksiForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['status']
