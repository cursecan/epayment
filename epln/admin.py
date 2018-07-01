from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Product, Transaksi, ResponseTransaksi, TransaksiRb, ResponseTransaksiRb
from .resources import ProductResource, TransaksiResource

def make_published(modeladmin, request, queryset):
    queryset.update(active=True)
make_published.short_description = "Mark selected product as published"

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    class Meta:
        model = Product
    list_display = ['nama_produk', 'kode_produk', 'nominal', 'price','parse_text', 'active']
    resource_class = ProductResource
    list_filter = ['active']
    actions = [make_published]


@admin.register(Transaksi)
class TransaksiAdmin(ImportExportModelAdmin):
    class Meta:
        model = Transaksi
    resource_class = TransaksiResource
    list_display = ['trx_code', 'product', 'phone', 'price', 'status', 'user', 'get_response','timestamp','update']
    list_filter = ['status']
    search_fields = ['trx_code', 'phone']

# admin.site.register(Product)
admin.site.register(TransaksiRb)
admin.site.register(ResponseTransaksi)
admin.site.register(ResponseTransaksiRb)
