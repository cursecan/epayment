from rest_framework import serializers
from django.contrib.auth.models import User

from mpulsa.models import Product, Transaksi

# SERIALIZER LIST PRODUK
class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'kode_internal', 'nominal', 'price']


# SERIALIZER LIST TRANSAKSI
class TransaksiListSerializer(serializers.ModelSerializer):
    saldo = serializers.SerializerMethodField()
    nominal = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()
    # status = serializers.SerializerMethodField()
    class Meta:
        model = Transaksi
        fields = ['id', 'trx_code', 'product', 'phone', 'user', 'pembukuan', 'saldo', 'price', 'nominal', 'info', 'status']

    def get_saldo(self, obj):
        user = obj.user
        user.refresh_from_db()
        return user.profile.saldo

    def get_nominal(self, obj):
        return obj.product.nominal
    
    def get_info(self, obj):
        return obj.product.keterangan

    # def get_status(self, obj):
    #     trx = obj
    #     trx.refresh_from_db()
    #     return trx.status



#SERIALIZER CREATE TRANSAKSI (NOT AKTIF)
class TopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaksi
        fields = ['phone', 'product', 'user']

    def create(self, validated_data):
        pass
