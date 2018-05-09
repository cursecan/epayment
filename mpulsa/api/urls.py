from django.urls import path

from . import views

app_name = 'saldo_api'
urlpatterns = [
    path('operator/', views.OperatorListAPI.as_view(), name='operator'),
    path('produk/', views.ProductListApi.as_view(), name='produk'),
    path('produks/', views.ProductListingApi.as_view(), name='produk_list'),
    path('transaksi/', views.TransaksiListApi.as_view(), name='transaksi'),
    path('topup/', views.TopupCreateApiView.as_view(), name='topup'),
]