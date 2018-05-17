from rest_framework import serializers

from epln.models import Product, Transaksi, ResponseTransaksi

class ProductSrializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'kode_produk', 'nama_produk', 'parse_text', 'price']