from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .froms import TransaksiForm, ProductForm
from .models import Product, Transaksi, ResponseTransaksi, Operator
from .resources import ProductResource, TransaksiResource

# @admin.register(Operator)
# class OperatorAdmin(admin.ModelAdmin):
#     inlines = [PrefixNumberInline]
def make_published(modeladmin, request, queryset):
    queryset.update(active=True)
make_published.short_description = "Mark selected product as published"


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    form = ProductForm
    list_display = ['id','operator', 'kode_internal', 'nominal', 'price', 'keterangan', 'parse_text', 'active']
    resource_class = ProductResource
    list_filter = ['operator']
    actions = [make_published]


@admin.register(Transaksi)
class TransaksiAdmin(ImportExportModelAdmin):
    resource_class = TransaksiResource
    form = TransaksiForm
    list_display = ['trx_code', 'product', 'phone', 'price', 'status', 'user', 'get_response','timestamp','update']
    list_filter = ['status']
    search_fields = ['trx_code', 'phone']


admin.site.register(Operator)
# admin.site.register(Product)
# admin.site.register(Transaksi)
admin.site.register(ResponseTransaksi)
