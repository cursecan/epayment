from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Product, Operator

class ProductResource(resources.ModelResource):
    operator = fields.Field(column_name='operator', attribute='operator', widget=ForeignKeyWidget(Operator, 'kode'))
    class Meta:
        model = Product
        import_id_fields = ('kode_internal',)
        fields = [
            'kode_internal','operator','nominal','price',
            'kode_external','price_beli','keterangan'
        ]
        skip_unchanged = True
        report_skipped = False