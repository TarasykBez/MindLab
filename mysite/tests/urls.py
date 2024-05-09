# tests/urls.py
from django.urls import path

from . import views
from .views import test_list, test_detail, test_result, submit_answers

urlpatterns = [
    path('', test_list, name='test_list'),
    path('<int:test_id>/', test_detail, name='test_detail'),
    path('results/<int:test_id>/', test_result, name='test_result'),
    path('submit/<int:test_id>/', submit_answers, name='submit_answers'),
]
