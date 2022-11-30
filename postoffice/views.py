""" Build the (static) website for a specified po_box from postbox.   """

from django.shortcuts import render

from postcards.views import get_postcard, get_pobox

# viewer_data and pobox are both initialized when the pobox_id is assigned.
# As each sender is connected, update both viewer_data and pobox

def update_viewer_data(pobox_id, viewer_data):              # viewer_data sent back up as a json file from viewer.
    """viewer_data is {from_tel: card_spec} where card_spec is everything needed for play"""
    # Change pobox data_dict defintion to conform to this change
    pobox = get_pobox(pobox_id)
    assert(pobox['meta']['version']==1)
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
        













def get_po_box_uuid(from_tel, connector, connections):
    possibles = connections[from_tel]    
    po_box_uuids = [possibles[to_tel]['po_box_uuid'] for to_tel in possibles]
    for po_box_uuid in po_box_uuids:
        if po_box_uuid[0:4] == connector:
            return po_box_uuid

def build_view_dictionary(po_box_uuid, senders, post_office):
    reading_desk = {}
    po_box_sorted_by_senders = post_office[po_box_uuid]
    recently_played = load_recently_played_from_s3()
    for from_tel in po_box_sorted_by_senders:
        try:
            reading_desk[from_tel] = get_one_next_card(from_tel, po_box_sorted_by_senders, recently_played, senders)
        except IndexError:   # Newly connected sender has no cards?  Hit this Oct 1, but changed "connect" to try to eliminate it.
            continue
    return reading_desk


def get_audio_duration(card_audio_url):
    try:
        meta_url = card_audio_url.replace('.mp3', '.json')
        resp = requests.get(meta_url)
        audio_meta = json.loads(resp.content)
        audio_duration = int(audio_meta['duration'])
    except Exception:
        audio_duration = None
    return audio_duration

