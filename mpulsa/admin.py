from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Operator, PrefixNumber, Product, Transaksi, ResponseTransaksi
from .forms import ProductForm, TransaksiForm
from .resources import ProductResource, TransaksiResource

class PrefixNumberInline(admin.TabularInline):
    model = PrefixNumber
    extra = 1

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    inlines = [PrefixNumberInline]

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    form = ProductForm
    list_display = ['operator', 'kode_internal', 'nominal', 'price', 'keterangan']
    resource_class = ProductResource
    list_filter = ['operator']


@admin.register(Transaksi)
class TransaksiAdmin(ImportExportModelAdmin):
    resource_class = TransaksiResource
    form = TransaksiForm
    list_display = ['trx_code', 'product', 'phone', 'price', 'status', 'user', 'get_response','timestamp','update']
    list_filter = ['status']
    search_fields = ['trx_code', 'phone']


# admin.site.register(Product)
# admin.site.register(Transaksi)
admin.site.register(ResponseTransaksi)
