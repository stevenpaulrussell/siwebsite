""" Build the (static) website for a specified po_box from postbox.   """

from postoffice import saveget

# viewer_data and pobox are both initialized when the pobox_id is assigned.
# As each sender is connected, update both viewer_data and pobox


def update_pobox_new_card(from_tel, to_tel, pobox_id, card_id):
    pobox = saveget.get_pobox(pobox_id)        
    pobox['cardlists'][from_tel].append(card_id)
    viewer_data = saveget.get_viewer_data(pobox_id)
    update_viewer_data(pobox, viewer_data)
    saveget.save_pobox(pobox)
    saveget.save_viewer_data(viewer_data)


def played_it(pobox_id, card_id):
    pobox = saveget.get_pobox(pobox_id)
    viewer_data = saveget.get_viewer_data(pobox_id)
    card = saveget.get_postcard[card_id]
    from_tel = card['from_tel']
    card['play_count'] += 1
    viewer_data[from_tel]['play_count'] += 1
    update_viewer_data(pobox, viewer_data)


def update_viewer_data(pobox, viewer_data):              
    """viewer_data is {from_tel: card_spec} where card_spec is everything needed for play"""
    # Change pobox data_dict defintion to conform to this change
    for from_tel in pobox['cardlists']:
        cardlist = pobox['cardlists'][from_tel]
        if not cardlist:        # No new cards to show, so on to the next sender's list
            continue    
        # There is a new card in pobox if viewer needs one
        viewer_card = viewer_data.get(from_tel, {})     
        if not viewer_card or viewer_card['play_count'] > 0:  # If initializing, or current has been played
            new_card_id, cardlist = cardlist[0], cardlist[1:]

            old_card_id = viewer_data.get('card_id', None)
            # Archive the old_card_id into some new data structure for each (receiver?).  Watch for None value
            
            new_card = saveget.get_postcard(new_card_id)
            viewer_card['card_id'] = new_card_id
            viewer_card['play_count'] = 0
            viewer_card['profile_url'] = new_card['profile_url']
            viewer_card['image_url'] = new_card['image_url']
            viewer_card['audio_url'] = new_card['audio_url']
            viewer_data[from_tel] = viewer_card
        

