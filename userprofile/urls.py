from django.urls import path

from . import views

app_name = 'userprofile'

urlpatterns = [
    path('', views.userindex, name='index'),
    path('pulsa/', views.pulsaProdukView, name='pulsa_produk'),
    path('etrans/', views.etransProdukView, name='trans_produk'),
    path('listrik-token/', views.listrikProdView, name='listrik_produk'),
    path('trx/pulsa/', views.pulsaTrxView, name='pulsa_trx'),
    path('trx/etrans/', views.transTrxView, name='trans_trx'),
    path('checktrx/', views.checkTrxView, name='checktrx'),
]