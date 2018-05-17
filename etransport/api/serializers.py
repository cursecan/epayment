from rest_framework import serializers

from etransport.models import Operator, Product

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['id','kode', 'operator']

class ProdukSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'kode_internal','nominal', 'keterangan', 'price', 'parse_text']



