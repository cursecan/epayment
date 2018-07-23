from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Product, Transaksi

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        # import_id_fields = ('kode_internal',)
        fields = [
            'id','kode_produk','nama_produk','nominal','price', 'parse_text'
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