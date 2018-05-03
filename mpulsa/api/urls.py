from django.urls import path

from . import views

app_name = 'saldo_api'
urlpatterns = [
    path('produk/', views.ProductListApi.as_view(), name='produk'),
    path('transaksi/', views.TransaksiListApi.as_view(), name='transaksi'),
    path('topup/', views.TransaksiCreateApiView.as_view(), name='topup'),
    path('topup2/', views.TopupCreateApiView.as_view(), name='topup2'),
]