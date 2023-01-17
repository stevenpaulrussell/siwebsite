from django.urls import path

from postbox.views import pobox_id_if_good_passkey         # These urlpatterns move when viewer is separated

from .views import instructions_view, get_a_pobox_id, tickles


urlpatterns = [
    path('tickles', tickles, name='tickles'),
    path('validate_me/<from_tel>/<passkey>', pobox_id_if_good_passkey, name='validate_passkey'),   # RPC, returns a redirect to viewer_data/<pobox_id>
    path('get_a_pobox_id', get_a_pobox_id, name='get_a_pobox_id'),                    # URL used by postmaster (?) to get to form asking for passkey
    path('', instructions_view, name='home'),
    ]
