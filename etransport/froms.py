from django import forms

from .models import Transaksi, Product


# class TransaksiModelForm(forms.ModelForm):
#     class Meta:
#         model = Transaksi
#         fields = ['product', 'phone']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['operator','kode_internal', 'nominal', 'price', 'kode_external', 'keterangan', 'parse_text', 'active']

class TransaksiForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['trx_code','price','phone','status','user','pembukuan','catatan_modal']
