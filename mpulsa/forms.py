from django import forms

from .models import Transaksi, Product, Biller


class TransaksiModelForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['product', 'phone']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['kode_internal' ,'operator','type_layanan', 'nominal', 'price','biller', 'keterangan', 'parse_text', 'active']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['biller'].queryset = Biller.objects.filter(product__isnull=True)
        # if not user.is_staff:
        #     self.fields['user'].queryset = User.objects.filter(profile__profile_member__user=user, profile__active=True).order_by('username')
        #     self.fields['method_payment'].choices = (('MN', 'MANUAL PAYMENT'),)


class TransaksiForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['trx_code','product','price', 'phone', 'status', 'pembukuan', 'catatan_modal', 'user']

