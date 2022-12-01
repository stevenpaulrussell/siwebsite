""" Build the (static) website for a specified po_box from postbox.   """

from django.shortcuts import render

from filer import views as filerviews

from postmaster.postcards import get_postcard

# viewer_data and pobox are both initialized when the pobox_id is assigned.
# As each sender is connected, update both viewer_data and pobox

def update_viewer_data(pobox, viewer_data):              
    """viewer_data is {from_tel: card_spec} where card_spec is everything needed for play"""
    # Change pobox data_dict defintion to conform to this change
    for from_tel in pobox['cardlists']:
        card_list = pobox[from_tel]
        if not card_list:
            continue    
            # In the following, there is a new card if one is needed...
        viewer_card = viewer_data.get(from_tel, {})     
        if not viewer_card or viewer_card['play_count'] > 0:  # Just initializing, or need a new card (and there is one!)
            new_card_id, card_list = card_list[0], card_list[1:]

            old_card_id = viewer_data['card_id']
            # Archive the old_card_id into some new data structure for each (receiver?)
            
            new_card = get_postcard(new_card_id)
            viewer_card['card_id'] = new_card_id
            viewer_card['play_count'] = 0
            viewer_card['profile_url'] = new_card['profile_url']
            viewer_card['image_url'] = new_card['image_url']
            viewer_card['audio_url'] = new_card['audio_url']
    return viewer_data
        



def get_viewer_data(pobox_id):
    filerviews._load_a_thing_using_key(key=f'viewer_data_{pobox_id}')

def save_viewer_data(viewer_data):
    pobox_id = viewer_data['meta']['viewer_data']
    filerviews._save_a_thing_using_key(thing=viewer_data, key=f'viewer_data_{pobox_id}')

