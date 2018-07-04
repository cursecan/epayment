from django.contrib import admin


from .models import Game, Biller, Product, TransaksiRb, ResponseTransaksiRb


admin.site.register(Game)
admin.site.register(Biller)
admin.site.register(Product)
admin.site.register(TransaksiRb)
admin.site.register(ResponseTransaksiRb)