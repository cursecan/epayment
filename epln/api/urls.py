from django.urls import path

from . import views

app_name = 'pln_api'
urlpatterns = [
    path('produk/', views.ProductsListApi.as_view(), name='produk'),
    path('topup/', views.TopupTokenListrikView.as_view(), name='topup'),
    path('topup_pln_rb/', views.TopupTokenListrik_RajaBillerView.as_view(), name='topup_pnl_rb'),
]