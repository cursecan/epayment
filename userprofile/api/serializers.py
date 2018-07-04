from rest_framework import serializers

from userprofile.models import Profile, PembukuanTransaksi
from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['telegram', 'email_confirmed', 'phone']


class PembukuanSerializer(serializers.ModelSerializer):
    telegram = serializers.SerializerMethodField()
    trx = serializers.SerializerMethodField()
    class Meta:
        model = PembukuanTransaksi
        fields = ['id','debit', 'kredit', 'balance', 'telegram', 'status_type', 'timestamp', 'trx']

    def get_telegram(self, obj):
        return obj.user.profile.telegram

    def get_trx(self, obj):
        # print(obj.id)
        try :
            bk = PembukuanTransaksi.objects.get(pembukuantransaksi__id=obj.id)
        
            if bk.transaksi:
                return bk.transaksi.trx_code
            elif bk.bukutrans:
                return bk.bukutrans.trx_code
            elif bk.bukupln :
                return bk.bukupln.trx_code
            elif bk.mpulsa_rbbuku_transaksi :
                return bk.mpulsa_rbbuku_transaksi.trx_code
            elif bk.epln_rbbuku_transaksi :
                return bk.epln_rbbuku_transaksi.trx_code
            elif bk.egame_rbbuku_transaksi :
                return bk.egame_rbbuku_transaksi.trx_code
            else:
                return bk.etrans_rbbuku_transaksi.trx_code


        except :
            return None


class PembukuanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PembukuanTransaksi
        fields = ['confrmed']



class UserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()
    telegram = serializers.SerializerMethodField()
    saldo = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'first_name', 'phone', 'telegram', 'saldo']

    def get_phone(self, obj):
        return obj.profile.phone

    def get_telegram(self, obj):
        return obj.profile.telegram

    def get_saldo(self, obj):
        return obj.profile.saldo