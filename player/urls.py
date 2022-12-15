from django.urls import path
from .views import instructions_view, make_connection_view, show_postcards_view, test_a_postcard_view

urlpatterns = [
    path('postbox/<po_box_uuid>', show_postcards_view, name='viewer'),
    path('test/<test_id>', test_a_postcard_view, name='test_viewer'),
    path('connect', make_connection_view, name='to_connect'),
    path('', instructions_view, name='home'),
    ]