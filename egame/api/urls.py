from django.urls import path

from . import views

app_name = 'egame_api'
urlpatterns = [
    path('game/', views.GameListApi.as_view(), name='game_list'),
    path('produk-game/', views.ProductListApi.as_view(), name='produk'),
    path('topup-game/', views.TopupCreateApiView_Rajabiller.as_view(), name='topup_game'),
]