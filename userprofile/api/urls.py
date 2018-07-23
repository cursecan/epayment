from django.urls import path

from . import views
app_name = 'userprofile_api'
urlpatterns = [
    path('profile/update/<str:token_code>/', views.ProfileUpdateView.as_view(), name='update-profile'),
    path('user/', views.UserListView.as_view(), name='user'),
    path('piutang-user/', views.PiutangUserView.as_view(), name='user_piutang'),
    path('unconfirm/', views.PembukuanPayReverseView.as_view(), name='list_unconfirm'),
    path('unconfirm/<int:id>/update/', views.PembukuanUpdateApi.as_view(), name='unconfirm_update'),
]