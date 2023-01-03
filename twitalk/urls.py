from django.urls import path

from .views import accept_media

urlpatterns = [
    path('accept_media', accept_media, name='accept_media'),                               
    ]