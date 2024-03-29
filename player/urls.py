from django.urls import path

from postbox.views import played_this_card                 # These urlpatterns move when viewer is separated
from postbox.views import return_playable_viewer_data      # These urlpatterns move when viewer is separated

from .views import show_postcards_view


urlpatterns = [
    path('played/<pobox_id>/<card_id>', played_this_card, name='played_it'),                               # RPC to postbox, purpose as stated
    path('viewer_data/<pobox_id>', return_playable_viewer_data, name='viewer_data'),            # RPC, asks for new data & as check-in
    path('postbox/<pobox_id>', show_postcards_view, name='viewer'),                   # URL used by browser to see the basic postcards view
    ]
