from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .froms import TransaksiForm, ProductForm
from .models import Product, Transaksi, ResponseTransaksi, Operator, Biller, TransaksiRb, ResponseTransaksiRb
from .resources import ProductResource, TransaksiResource


def make_published(modeladmin, request, queryset):
    queryset.update(active=True)
make_published.short_description = "Mark selected product as published"


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    form = ProductForm
    list_display = ['operator', 'kode_internal', 'nominal', 'price', 'price_beli','benefit','biller', 'parse_text', 'active']
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


@admin.register(Biller)
class BillerAdmin(admin.ModelAdmin):
    list_display = [
        'nama', 'code', 'biller', 'price'
    ]
    class Meta:
        model = Biller


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ['kode', 'operator', 'active']
    class Meta:
        model= Operator


@admin.register(TransaksiRb)
class TransaksiRbAdmin(admin.ModelAdmin):
    list_display = ['trx_code', 'product', 'phone', 'price', 'status', 'user', 'get_response','timestamp','update']
    list_filter = ['status']
    search_fields = ['trx_code', 'phone']

    class Meta:
        model = TransaksiRb

# admin.site.register(Operator)
# admin.site.register(Biller)
# admin.site.register(TransaksiRb)
admin.site.register(ResponseTransaksiRb)
admin.site.register(ResponseTransaksi)
