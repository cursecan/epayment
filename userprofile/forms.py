from django import forms


from .models import Profile, PembukuanTransaksi


class PembukuanTransaksiForm(forms.ModelForm):
    class Meta:
        model = PembukuanTransaksi
        fields = ['user', 'debit', 'kredit', 'balance','keterangan']