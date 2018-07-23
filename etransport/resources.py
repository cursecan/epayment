from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Product, Operator, Transaksi

class ProductResource(resources.ModelResource):
    operator = fields.Field(column_name='operator', attribute='operator', widget=ForeignKeyWidget(Operator, 'kode'))
    class Meta:
        model = Product
        fields = [
            'id',
            'kode_internal','operator','nominal','price',
            'kode_external','keterangan', 'parse_text'
        ]
        skip_unchanged = True
        report_skipped = False


class TransaksiResource(resources.ModelResource):
    class Meta:
        model = Transaksi
        fields = [
            'trx_code','product','price','phone',
            'status','user','pembukuan','timestamp','update'
        ]