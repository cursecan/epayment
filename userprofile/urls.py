from django.urls import path

from . import views

app_name = 'userprofile'

urlpatterns = [
    path('', views.userindex, name='index'),
    path('transaksi/', views.trx_produk_all, name='transaksi'),
    path('transaksi/mpulsa/<int:id>/', views.trx_detail_pulsa_view, name='pulsa_trx'),
    path('transaksi/mpulsa/<int:id>/f/', views.trx_edit_pulsa_view, name='pulsa_failed'),
    path('transaksi/pln/<int:id>/', views.trx_detail_pln_view, name='pln_trx'),
    path('transaksi/transport/<int:id>/', views.trx_detail_trans_view, name='trans_trx'),
    path('checktrx/', views.checkTrxView, name='checktrx'),
    path('sistemprice/', views.checkHargaView, name='price'),
]