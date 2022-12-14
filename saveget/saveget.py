from filer import exceptions as filerexceptions
from filer import views as filerviews


def update_sender_and_morsel(sender):  
    """Morsel a read-only, limited-info represent of sender for twilio processing."""
    morsel = make_morsel(sender)
    filerviews._save_a_thing_using_key(thing=morsel, key=f'free_tier/{sender["from_tel"]}')
    save_sender(sender)

def make_morsel(sender):            #  This separated from update_sender_and_morsel for test.
    morsel =  {}
    for to_tel in sender['conn']: 
        morsel[to_tel] = {}
        morsel[to_tel]['from'] = sender['conn'][to_tel]['from']
        morsel[to_tel]['to'] = sender['conn'][to_tel]['to']
        morsel[to_tel]['have_viewer'] = 'HaveViewer' if sender['conn'][to_tel]['pobox_id'] else False
    return morsel


    
def get_sender(from_tel):
    return filerviews._load_a_thing_using_key(key=f'sender/{from_tel}')
def save_sender(sender):
    filerviews._save_a_thing_using_key(thing=sender, key=f'sender/{sender["from_tel"]}')


def get_pobox(pobox_id):
    return filerviews._load_a_thing_using_key(key=f'pobox_{pobox_id}')
def save_pobox(pobox):
    pobox_id = pobox['meta']['pobox_id']
    filerviews._save_a_thing_using_key(thing=pobox, key=f'pobox_{pobox_id}')
def delete_pobox(pobox):
    pobox_id = pobox['meta']['pobox_id']
    filerviews._delete_a_thing_using_key(key=f'pobox_{pobox_id}')


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
def delete_viewer_data(viewer_data):
    pobox_id = viewer_data['meta']['pobox_id']
    filerviews._delete_a_thing_using_key(key=f'viewer_data_{pobox_id}')


def delete_twilio_new_sender(sender):
    filerviews._delete_a_thing_using_key(key=f'new_sender/{sender["from_tel"]}')

def clear_sqs_and_s3_for_testing(sender):
    filerviews.clear_the_read_bucket()
    filerviews.clear_the_sqs_queue_TEST_SQS()



def get_one_sqs_cmd():
    """In TEST, CMD_SQS and ADMIN queue urls both map to CMD_URL read here. 
        In PRODUCTION,  ADMIN is not read by these 'web' programs"""
    return filerviews.get_an_sqs_message()

def _test_send_an_sqs_cmd(message):
    """This used only for testing."""
    filerviews.send_an_sqs_message(message, QueueUrl=filerviews.TEST_SQS)


    