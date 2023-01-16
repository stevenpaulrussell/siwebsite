from django.urls import path

from .views import accept_media, twi_recorder

urlpatterns = [
    path('accept_media', accept_media, name='accept_media'),                               
    path('twi_recorder', twi_recorder, name='twi_recorder'),                               
    ]