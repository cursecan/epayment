from django.urls import path

from . import views

app_name = 'userprofile'

urlpatterns = [
    path('', views.userindex, name='index'),
    path('transaksi/', views.trx_produk_all, name='transaksi'),
    path('transaksi/dataset/', views.trx_dataset, name='trx_dataset'),
    path('transaksi/mpulsa/<int:id>/', views.trx_detail_pulsa_view, name='pulsa_trx'),
    path('transaksi/mpulsa-rb/<int:id>/', views.trx_detail_pulsa_rajabiler_view, name='pulsa_trx_rb'),
    path('transaksi/mpulsa/<int:id>/f/', views.trx_edit_pulsa_view, name='pulsa_failed'),
    path('transaksi/mpulsa-rb/<int:id>/f/', views.trx_edit_pulsa_view_rajabiller, name='pulsa_failed_rajabiler'),
    path('transaksi/pln/<int:id>/', views.trx_detail_pln_view, name='pln_trx'),
    path('transaksi/transport/<int:id>/', views.trx_detail_trans_view, name='trans_trx'),

    path('detail-pendapatan/', views.pendapatanAgen, name='pendapatan_agen'),
    path('usergroups/', views.member_View, name='member_view'),
    path('usergroups/<int:id>/add-saldo/', views.tambahSaldo_view, name='tambah_saldo'),
    path('usergroups/collectrasio/', views.colrasio_dataset, name='collect_rasio'),
    path('transaction-check/', views.checkTrxView, name='checktrx'),
    path('sistemprice/', views.checkHargaView, name='price'),
    path('price-rajabiller/', views.checkHargaViewRajabiller, name='price_rajabiller'),

    path('produk/', views.produk_View, name='produk'),
    path('payroll/', views.generate_payroll, name='payroll'),
]