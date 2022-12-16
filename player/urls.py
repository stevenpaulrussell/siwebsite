from django.urls import path

from postoffice.cmdline import played_this_card
from .views import instructions_view, make_connection_view, show_postcards_view


urlpatterns = [
    path('played/<card_id>', played_this_card, name='played_it'),
    path('postbox/<pobox_id>', show_postcards_view, name='viewer'),
    path('connect', make_connection_view, name='to_connect'),
    path('', instructions_view, name='home'),
    ]