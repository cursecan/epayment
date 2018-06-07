from django import forms

from .models import Transaksi, Product


class TransaksiModelForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['product', 'phone']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['kode_internal' ,'operator','type_layanan', 'nominal', 'price','biller', 'keterangan', 'parse_text', 'active']

class TransaksiForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['trx_code','product','price', 'phone', 'status', 'pembukuan', 'catatan_modal', 'user']

