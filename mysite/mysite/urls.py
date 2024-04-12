from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
# Імпортуйте налаштування та static у разі роботи з медіафайлами
from django.conf import settings
from django.conf.urls.static import static

def index(request):
    return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('tests/', include(('tests.urls', 'tests'), namespace='tests')),
    path('', index, name='index'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
