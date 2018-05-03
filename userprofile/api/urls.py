from django.urls import path

from . import views
app_name = 'userprofile_api'
urlpatterns = [
    path('profile/update/<str:token_code>/', views.ProfileUpdateView.as_view(), name='update-profile'),
    
]