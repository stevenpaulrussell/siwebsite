from filer import exceptions as filerexceptions
from filer import views as filerviews

    
def get_sender(from_tel):
    return filerviews._load_a_thing_using_key(key=f'sender/{from_tel}')
def save_sender(sender):
    filerviews._save_a_thing_using_key(thing=sender, key=f'sender/{sender["from_tel"]}')


def get_pobox(pobox_id):
    return filerviews._load_a_thing_using_key(key=f'pobox_{pobox_id}')
def save_pobox(pobox):
    pobox_id = pobox['meta']['pobox_id']
    filerviews._save_a_thing_using_key(thing=pobox, key=f'pobox_{pobox_id}')


def get_postcard(card_id):
    return filerviews._load_a_thing_using_key(key=f'card_{card_id}')
def save_postcard(postcard):
    card_id = postcard['card_id']
    filerviews._save_a_thing_using_key(thing=postcard, key=f'card_{card_id}')


def get_passkey_dictionary(from_tel):
    try:
        return filerviews._load_a_thing_using_key(f'passkey_{from_tel}')
    except filerexceptions.S3KeyNotFound:
        return None
def save_passkey_dictionary(passkey):
    from_tel =  passkey['from_tel']
    filerviews._save_a_thing_using_key(thing=passkey, key=f'passkey_{from_tel}')  


def get_viewer_data(pobox_id):
    return filerviews._load_a_thing_using_key(key=f'viewer_data_{pobox_id}')
def save_viewer_data(viewer_data):
    pobox_id = viewer_data['meta']['pobox_id']
    filerviews._save_a_thing_using_key(thing=viewer_data, key=f'viewer_data_{pobox_id}')

def save_morsel(sender, morsel):
    filerviews._save_a_thing_using_key(thing=morsel, key=f'free_tier/{sender["from_tel"]}')

def delete_twilio_new_sender(sender):
    filerviews._delete_a_thing_using_key(key=f'new_sender/{sender["from_tel"]}')

