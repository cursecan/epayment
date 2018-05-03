from django.contrib import admin

from .models import Operator, PrefixNumber, Product, Transaksi, ResponseTransaksi
from .forms import ProductForm, TransaksiForm

class PrefixNumberInline(admin.TabularInline):
    model = PrefixNumber
    extra = 1

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    inlines = [PrefixNumberInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['operator', 'kode_internal', 'nominal', 'price', 'keterangan']


@admin.register(Transaksi)
class TransaksiAdmin(admin.ModelAdmin):
    form = TransaksiForm
    list_display = ['trx_code', 'product', 'phone', 'price', 'status', 'user', 'get_response']

# admin.site.register(Product)
# admin.site.register(Transaksi)
# admin.site.register(ResponseTransaksi)
