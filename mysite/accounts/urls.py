from django.urls import path
from . import views
from .views import register, AuthView

urlpatterns = [
    path('register/', register, name='register'),
    path('additional_info/', views.additional_info, name='additional_info'),
    path('email_verification_sent/', views.email_verification_sent, name='email_verification_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', AuthView.as_view(), name='login'),
    path('account/', views.account, name='account')
]
