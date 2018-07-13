from django.contrib import admin


from .models import Game, Biller, Product, TransaksiRb, ResponseTransaksiRb


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'nama_game', 'active', 'timestamp', 'update'
    ]
    class Meta:
        model = Game

@admin.register(Biller)
class BillerAdmin(admin.ModelAdmin):
    list_display = [
        'nama', 'code', 'biller', 'price'
    ]
    class Meta:
        model = Biller


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'developer','kode_internal', 'keterangan', 'price', 'biller','benefit', 'active', 'timestamp'
    ]
    list_filter = ['developer']
    class Meta:
        model = Product


@admin.register(TransaksiRb)
class TransaksiRbAdmin(admin.ModelAdmin):
    list_display = ['trx_code', 'product', 'phone', 'price', 'status', 'user', 'get_response','timestamp','update']
    list_filter = ['status']
    search_fields = ['trx_code', 'phone']
    class Meta:
        model = TransaksiRb

admin.site.register(ResponseTransaksiRb)