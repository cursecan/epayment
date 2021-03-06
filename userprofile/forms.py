from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, PembukuanTransaksi, UserPayment, PembukuanPartner

# REGULAR SINGUP FORM
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

    def clean_username(self):
        return self.cleaned_data.get('username').lower()

    def clean_email(self):
        return self.cleaned_data.get('email').lower()

    def clean_first_name(self):
        return self.cleaned_data.get('first_name').lower()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name').lower()


# MEMBER CREATE USER
class UserCreatorForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_username(self):
        return self.cleaned_data.get('username').lower()

    def clean_email(self):
        return self.cleaned_data.get('email').lower()

    def clean_first_name(self):
        return self.cleaned_data.get('first_name').lower()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name').lower()

    def clean_password1(self):
        return 'obj09871'

    def clean_password2(self):
        return 'obj09871'


class PembukuanTransaksiForm(forms.ModelForm):
    class Meta:
        model = PembukuanTransaksi
        fields = ['user', 'debit', 'kredit', 'balance','status_type','keterangan']



class AddSaldoForm(forms.ModelForm):
    class Meta:
        model = PembukuanTransaksi
        fields = ['debit', 'keterangan']


class AddSaldoNewForm(forms.ModelForm):
    class Meta:
        model = UserPayment
        fields = ['user', 'debit', 'method_payment', 'berita_acara']

    def __init__(self, user, *args, **kwargs):
        super(AddSaldoNewForm, self).__init__(*args, **kwargs)
        if not user.is_staff:
            self.fields['user'].queryset = User.objects.filter(profile__profile_member__user=user, profile__active=True).order_by('username')
            self.fields['method_payment'].choices = (('MN', 'MANUAL PAYMENT'),)


class ModifyLimit(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['limit']

    def clean_limit(self):
        limit = self.cleaned_data.get('limit')
        if limit > 0:
            limit = -limit
        return limit

class PembukuanPartnerForm(forms.ModelForm):
    class Meta:
        model = PembukuanPartner
        fields = [
            'partner', 'nominal'
        ]

    def __init__(self, user, *args, **kwargs):
        super(PembukuanPartnerForm, self).__init__(*args, **kwargs)
        if user.is_staff:
            self.fields['partner'].queryset = User.objects.filter(profile__agen=True)
        # else:
        #     self.fields['partner'].queryset = None

    def clean_nominal(self):
        nominal = self.cleaned_data.get('nominal', 0)
        if nominal <= 0 :
            raise forms.ValidationError('Nominal harus positif.')
        return nominal