from django.urls import path

from . import views

app_name = 'transport_api'
urlpatterns = [
    path('operator/', views.OperatorListView.as_view(), name='operator'),
    path('produk/', views.ProdukListView.as_view(), name='produk'),
]