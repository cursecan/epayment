from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Product, Operator, Transaksi

class ProductResource(resources.ModelResource):
    operator = fields.Field(column_name='operator', attribute='operator', widget=ForeignKeyWidget(Operator, 'kode'))
    class Meta:
        model = Product
        # import_id_fields = ('kode_internal',)
        fields = [
            'id',
            'kode_internal','operator','type_layanan','nominal','price',
            'kode_external','price_beli','keterangan', 'parse_text'
        ]
        skip_unchanged = True
        report_skipped = False
        export_order = ('id',)


class TransaksiResource(resources.ModelResource):
    class Meta:
        model = Transaksi
        fields = [
            'trx_code','product','price','phone',
            'status','user','pembukuan','timestamp','update'
        ]