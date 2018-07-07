from django.urls import path

from . import views

app_name = 'userprofile'

urlpatterns = [
    path('', views.userindex, name='index'),
    path('transaksi/', views.trx_produk_all, name='transaksi'),
    path('transaksi/dataset/', views.trx_dataset, name='trx_dataset'),
    # url trx pulsa
    path('transaksi/mpulsa/<int:id>/', views.trx_detail_pulsa_view, name='pulsa_trx'),
    path('transaksi/mpulsa-rb/<int:id>/', views.trx_detail_pulsa_rajabiler_view, name='pulsa_trx_rb'),
    path('transaksi/mpulsa/<int:id>/f/', views.trx_edit_pulsa_view, name='pulsa_failed'),
    path('transaksi/mpulsa-rb/<int:id>/f/', views.trx_edit_pulsa_view_rajabiller, name='pulsa_failed_rajabiler'),
    # url trx pln
    path('transaksi/pln/<int:id>/', views.trx_detail_pln_view, name='pln_trx'),
    path('transaksi/pln-rb/<int:id>/', views.trx_detail_pln_rb_view, name='pln_trx_rb'),
    path('transaksi/pln-rb/<int:id>/f/', views.trx_edit_pln_view_rajabiller, name='pln_failed_rb'),
    # url trx game
    path('transaksi/game-rb/<int:id>/', views.trx_detail_game_rb_view, name='game_trx_rb'),
    path('transaksi/game-rb/<int:id>/f/', views.trx_edit_game_view_rajabiller, name='game_failed_rb'),
    # url trx etrans
    path('transaksi/transport-rb/<int:id>/f/', views.trx_edit_trans_view_rajabiller, name='trans_failed_rb'),
    path('transaksi/transport/<int:id>/', views.trx_detail_trans_view, name='trans_trx'),
    path('transaksi/transport-rb/<int:id>/', views.trx_detail_trans_rb_view, name='trans_trx_rb'),
    path('transaksi/transport-rb/<int:id>/f/', views.trx_edit_trans_view_rajabiller, name='trans_failed_rb'),

    path('detail-pendapatan/', views.pendapatanAgen, name='pendapatan_agen'),
    path('usergroups/', views.member_View, name='member_view'),
    path('usergroups/<int:id>/add-saldo/', views.tambahSaldo_view, name='tambah_saldo'),
    path('usergroups/add-saldo/', views.tambahSaldo2_view, name='tambah_saldo2'),
    path('usergroups/collectrasio/', views.colrasio_dataset, name='collect_rasio'),
    path('transaction-check/', views.checkTrxView, name='checktrx'),
    path('sistemprice/', views.checkHargaView, name='price'),
    path('price-rajabiller/', views.checkHargaViewRajabiller, name='price_rajabiller'),

    path('produk/', views.produk_View, name='produk'),
    path('payroll/', views.generate_payroll, name='payroll'),
    path('update-limit/<int:id>/update/', views.limitModifierView, name='update_limit_saldo'),
    path('bulk/trx-mpulsa-status/', views.bulk_update_trx_mpulsa, name='bulk_trx_mpulsa_check'),
    path('bulk/trx-mgame-status/', views.bulk_update_trx_mgame, name='bulk_trx_mgame_check'),
]