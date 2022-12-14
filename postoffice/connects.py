
import time
import uuid

from saveget import saveget


def connect_viewer(sender, to_tel):
    """With new uuid, initialize the pobox and an empty viewer_data, update the viewer_data from the new pobox"""
    if to_tel not in sender['conn']:
        return None
    pobox_id = sender['conn'][to_tel]['pobox_id']
    if not pobox_id:
        # assign new pobox_id to sender
        pobox_id = str(uuid.uuid4())
        sender['conn'][to_tel]['pobox_id'] = pobox_id
        # make pobox and an empty viewer data, which will contain nothing until a call from postbox  
        from_tel = sender['from_tel']
        meta = dict(version=1, pobox_id=pobox_id, key_operator=from_tel, heard_from=None)
        recent_card = sender['conn'][to_tel]['recent_card_id']
        cardlist = {from_tel: [recent_card,]}               # Couldn't use dict(from_tel=..) as that made from_tel a literal
        pobox = dict(meta=meta, cardlists=cardlist)
        viewer_data = dict(meta=dict(version=1, pobox_id=pobox_id))
        # Save sender, morsel, pobox, and an empty viewer_data
        saveget.update_sender_and_morsel(sender)    # pobox_id is set
        saveget.save_pobox(pobox)         # pobox is made and immediately used to update the new viewer_data
        saveget.save_viewer_data(viewer_data)       # viewer_data is made from the new pobox
    return pobox_id


def disconnect_from_viewer(sender, to_tel):
    """Delete from sender, pobox, and viewer_data, ... if there is a pobox"""
    if not sender['conn'][to_tel]['pobox_id']:
        return
    # Reset sender...[pobox_id] to None. 
    pobox_id, sender['conn'][to_tel]['pobox_id'] = sender['conn'][to_tel]['pobox_id'],  None
    saveget.update_sender_and_morsel(sender)    
    # Clear sender from the pobox and view_data, maybe send a message to the key_operator
    pobox, viewer_data = saveget.get_pobox(pobox_id), saveget.get_viewer_data(pobox_id)
    from_tel = sender['from_tel']
    pobox['cardlists'].pop(from_tel)
    if from_tel in viewer_data:             # Not True in unit test since viewer_data is updated only in module pobox
        viewer_data.pop(from_tel)
    if pobox['cardlists'] == {}:
        saveget.delete_pobox(pobox)
        saveget.delete_viewer_data(viewer_data)
    else:
        saveget.save_pobox(pobox)
        saveget.save_viewer_data(viewer_data)
    # Send messages to key_operator, admin???
    key_operator = pobox['meta']['key_operator']


def connect_joiner_to_lead_sender_pobox(joiner, lead_sender, joiner_to_tel, to_tel):
    """from_tel, to_tel pair determines a unique connection.  Map the request_sender connection
    to the pobox the lead_sender from_tel, to_tel points to.  Update the pobox to store those 
    postcards.
    """
    wanted_pobox_id = lead_sender['conn'][to_tel]['pobox_id']   # This pobox_id is the one being added to.
    to_name = lead_sender['conn'][to_tel]['to']
    joiner['conn'][joiner_to_tel]['pobox_id'] = wanted_pobox_id
    joiner['conn'][joiner_to_tel]['to'] = to_name
    pobox = saveget.get_pobox(wanted_pobox_id)
    pobox['cardlists'][joiner['from_tel']] = []
    saveget.save_pobox(pobox)
    saveget.update_sender_and_morsel(joiner)
    message = f'Successfully connected {joiner["from_tel"]} to {to_name}'
    return message


def get_passkey(from_tel):
    """Return both the passkey and the to_tel associated, to allow matching for security or for to_tel ident."""
    passkey_dictionary = saveget.get_passkey_dictionary(from_tel)
    if passkey_dictionary and time.time() < passkey_dictionary['expire']:
        return passkey_dictionary['passkey'], passkey_dictionary['to_tel']
    
def _set_passkey(from_tel, to_tel, duration=24):
    """Used only for test in this module"""
    expire = time.time() + duration*60*60
    passkey = str(uuid.uuid4())[0:4]
    current_key = dict(passkey=passkey, from_tel=from_tel, to_tel=to_tel, expire=expire)
    saveget.save_passkey_dictionary(current_key)
    



    