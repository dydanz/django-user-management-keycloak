from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('api/profile/', views.get_user_profile, name='api_profile'),
    path('api/toggle-mfa/', views.toggle_mfa, name='toggle_mfa'),
    path('api/update-phone/', views.update_phone, name='update_phone'),
] 