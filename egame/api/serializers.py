from rest_framework import serializers
from django.contrib.auth.models import User

from egame.models import Product, Game

# SERIALIZER LIST PRODUK
class ProductListSerializer(serializers.ModelSerializer):
    bill = serializers.SerializerMethodField()
    panduan = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'kode_internal', 'nominal', 'price', 'keterangan', 'parse_text', 'bill', 'panduan']

    def get_bill(self, obj):
        return obj.biller.biller

    def get_panduan(self, obj):
        return obj.developer.help_text


# SERIALIZER LIST GAME
class GameOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'code', 'nama_game']

