""" Build the (static) website for a specified po_box from postbox.   """

from django.shortcuts import render

from filer import views as filerviews


# viewer_data and pobox are both initialized when the pobox_id is assigned.
# As each sender is connected, update both viewer_data and pobox

def update_viewer_data(pobox, viewer_data):              
    """viewer_data is {from_tel: card_spec} where card_spec is everything needed for play"""
    # Change pobox data_dict defintion to conform to this change
    for from_tel in pobox['cardlists']:
        cardlist = pobox['cardlists'][from_tel]
        if not cardlist:
            continue    
            # In the following, there is a new card if one is needed...
        viewer_card = viewer_data.get(from_tel, {})     
        if not viewer_card or viewer_card['play_count'] > 0:  # Just initializing, or need a new card (and there is one!)
            new_card_id, cardlist = cardlist[0], cardlist[1:]
    
            old_card_id = viewer_data.get('card_id', None)
            # Archive the old_card_id into some new data structure for each (receiver?).  Watch for None value
            
            new_card = get_postcard(new_card_id)
            viewer_card['card_id'] = new_card_id
            viewer_card['play_count'] = 0
            viewer_card['profile_url'] = new_card['profile_url']
            viewer_card['image_url'] = new_card['image_url']
            viewer_card['audio_url'] = new_card['audio_url']
            viewer_data[from_tel] = viewer_card
    return viewer_data
        

def get_viewer_data(pobox_id):
    return filerviews._load_a_thing_using_key(key=f'viewer_data_{pobox_id}')

def save_viewer_data(viewer_data):
    pobox_id = viewer_data['meta']['pobox_id']
    filerviews._save_a_thing_using_key(thing=viewer_data, key=f'viewer_data_{pobox_id}')

def get_postcard(card_id):
    return filerviews._load_a_thing_using_key(key=f'card_{card_id}')

