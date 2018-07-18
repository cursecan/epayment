from rest_framework import serializers

from etransport.models import Operator, Product

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['id','kode', 'operator']

class ProdukSerializer(serializers.ModelSerializer):
    help_text = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'kode_internal','nominal', 'keterangan', 'price', 'parse_text', 'help_text']


    def get_help_text(self, obj):
        return obj.operator.help_text
    



