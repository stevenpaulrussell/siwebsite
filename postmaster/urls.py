from django.urls import path

from .views import instructions_view, tickles
from postoffice.views import get_a_pobox_id


urlpatterns = [
    path('tickles', tickles, name='tickles'),
    path('get_a_pobox_id', get_a_pobox_id, name='get_a_pobox_id'),                    # URL used by postmaster (?) to get to form asking for passkey
    path('', instructions_view, name='home'),
    ]
