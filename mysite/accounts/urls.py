from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views import test_results_view, show_captcha

app_name = 'accounts'

urlpatterns = (
    path('register/', views.register, name='register'),
    path('additional_info/', views.additional_info, name='additional_info'),
    path('email_verification_sent/', views.email_verification_sent, name='email_verification_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', views.AuthView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account, name='account'),
    path('account/reset_data/', views.account_reset_data, name='account_reset_data'),
    path('account/test_results/', test_results_view, name='test_results'),
    path('captcha/', show_captcha, name='show_captcha'),
    # Вказуємо шляхи для процесу скидання паролю
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),


)

