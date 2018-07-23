from django.urls import path

from . import views

app_name = 'transport_api'
urlpatterns = [
    path('operator/', views.OperatorListView.as_view(), name='operator'),
    path('produk/', views.ProdukListView.as_view(), name='produk'),
    path('produk-detail/', views.ProductListingApi.as_view(), name='produks'),
    path('topup/', views.TopupEtransport.as_view(), name='topup'),
    path('topup_trans_rb/', views.TopupEtransportRajaBiller.as_view(), name='topup_rb'),
]