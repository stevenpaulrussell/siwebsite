
import time
import uuid

from . import postcards

from postoffice.views import update_viewer_data, save_viewer_data



def check_passkey(from_tel, possible_key):
    passkey, to_tel = get_passkey(from_tel)
    if passkey == possible_key:
        return dict(to_tel=to_tel)
    else:
        return dict(error='xxx')    # Make a proper message back to the web or to the sender somehow... prefer the sender,
                        # but should run a check on the sender number since that might be the error!


def connect_viewer(sender, to_tel):
    pobox_id = sender['conn'][to_tel]['pobox_id']
    if not pobox_id:
        # assign new pobox_id to sender
        pobox_id = str(uuid.uuid4())
        sender['conn'][to_tel]['pobox_id'] = pobox_id
        # make pobox
        from_tel = sender['from_tel']
        meta = dict(version=1, pobox_id=pobox_id, key_operator=from_tel)
        recent_card = sender['conn'][to_tel]['recent_card_id']
        cardlist = {from_tel: [recent_card,]}               # Couldn't use dict(from_tel=..) as that made from_tel a literal
        pobox = dict(meta=meta, cardlists=cardlist)
        # make viewer_data  
        viewer_data = dict(meta=dict(version=1, pobox_id=pobox_id))
        update_viewer_data(pobox=pobox, viewer_data=viewer_data)
        # Save sender, pobox, viewer_data
        postcards.save_sender(sender)       # pobox_id is set
        postcards.save_pobox(pobox)         # pobox is made and immediately used to update the new viewer_data
        save_viewer_data(viewer_data)       # viewer_data is made from the new pobox
    return f'This a stand-in at postmaster.connect_viewer for the url for postbox: {pobox_id}'

    
def get_passkey(from_tel):
    """Return both the passkey and the to_tel associated, to allow matching for security or for to_tel ident."""
    current_key = postcards.get_passkey_dictionary(from_tel)
    if current_key and time.time() < current_key['expire']:
        return current_key['passkey'], current_key['to_tel']
    
def set_passkey(from_tel, to_tel, duration=24):
    """Stores a short-lived 'passkey' for both security and easy id of a to_tell when adding a sender.
    Each from_tel allowed a single passkey even if have multiple to_tel, but use case is ok. """
    expire = time.time() + duration*60*60
    passkey = str(uuid.uuid4())[0:4]
    current_key = dict(passkey=passkey, from_tel=from_tel, to_tel=to_tel, expire=expire)
    postcards.save_passkey_dictionary(current_key)
    return passkey

    


    