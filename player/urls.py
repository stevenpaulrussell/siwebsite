from django.urls import path

from postbox.cmdline import played_this_card                 # These urlpatterns move when viewer is separated
from postbox.cmdline import return_playable_viewer_data      # These urlpatterns move when viewer is separated
from postbox.cmdline import validate_passkey                 # These urlpatterns move when viewer is separated

from .views import instructions_view, get_a_pobox_id, show_postcards_view


urlpatterns = [
    path('played/<card_id>', played_this_card, name='played_it'),
    path('viewer_data/<pobox_id>', return_playable_viewer_data, name='viewer_data'),
    path('postbox/<pobox_id>', show_postcards_view, name='viewer'),
    path('validate_passkey/<from_tel>/<passkey>', validate_passkey, name='validate_passkey'),
    path('get_a_pobox_id', get_a_pobox_id, name='get_a_pobox_id'),
    path('', instructions_view, name='home'),
    ]