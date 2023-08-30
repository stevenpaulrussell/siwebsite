from filer import views as filerviews


def update_sender_and_morsel(sender):  
    """Morsel a read-only, limited-info represent of sender for twilio processing."""
    morsel = make_morsel(sender)
    filerviews._save_a_thing_using_key(thing=morsel, key=f'free_tier/{sender["tel_id"]}')
    save_sender(sender)

def make_morsel(sender):            #  This separated from update_sender_and_morsel for test.
    return sender['morsel']


    
def get_sender(tel_id):
    return filerviews._load_a_thing_using_key(key=f'sender/{tel_id}')
def save_sender(sender):
    filerviews._save_a_thing_using_key(thing=sender, key=f'sender/{sender["tel_id"]}')


def get_pobox(pobox_id):
    return filerviews._load_a_thing_using_key(key=f'pobox/pobox_{pobox_id}')
def save_pobox(pobox):
    pobox_id = pobox['pobox_id']
    filerviews._save_a_thing_using_key(thing=pobox, key=f'pobox/pobox_{pobox_id}')
def delete_pobox(pobox):
    pobox_id = pobox['pobox_id']
    filerviews._delete_a_thing_using_key(key=f'pobox/pobox_{pobox_id}')

def get_viewer_data(pobox_id):
    pobox = get_pobox(pobox_id)
    return pobox['viewer_data']


def get_postcard(card_id):
    return filerviews._load_a_thing_using_key(key=f'card/card_{card_id}')
def save_postcard(postcard):
    card_id = postcard['card_id']
    filerviews._save_a_thing_using_key(thing=postcard, key=f'card/card_{card_id}')


def get_polink(tel_id, svc_id, debug_string=None):
    key=f'polink/polink_{(tel_id, svc_id)}'
    result = filerviews._load_a_thing_using_key(key=key)
    if debug_string:
        print(f'\nget_polink debug {debug_string}... got: {tel_id, svc_id, result["pobox_id"]}')
    return result
def save_polink(polink, debug_string=None):
    tel_id = polink['tel_id']
    svc_id = polink['svc_id']
    key=f'polink/polink_{(tel_id, svc_id)}'
    filerviews._save_a_thing_using_key(thing=polink, key=key)
    if debug_string:
        print(f'\nsave_polink debug {debug_string}... saving: {tel_id, svc_id, polink["pobox_id"]}')



def get_passkey_dictionary(tel_id):
    try:
        return filerviews._load_a_thing_using_key(f'passkey/{tel_id}')
    except filerviews.S3KeyNotFound:
        return None
def save_passkey_dictionary(passkey):
    tel_id =  passkey['tel_id']
    filerviews._save_a_thing_using_key(thing=passkey, key=f'passkey/{tel_id}')  


def delete_twilio_new_sender(sender):
    filerviews._delete_a_thing_using_key(key=f'new_sender/{sender["tel_id"]}')

def clear_sqs_and_s3_for_testing(sender):
    filerviews.clear_the_read_bucket()
    filerviews.clear_the_sqs_queue_TEST_SQS()



def get_one_sqs_event():
    return filerviews.get_an_sqs_message()

def get_one_sqs_admin():
    return filerviews.get_an_sqs_message(QueueUrl=filerviews.ADMIN_URL)

def _test_send_an_sqs_event(message):
    """This used only for testing."""
    filerviews.send_an_sqs_message(message, QueueUrl=filerviews.EVENT_URL)


def nq_played_this_card(pobox_id, card_id):
    message = dict(
        pobox_id = pobox_id,
        card_id = card_id
    )
    filerviews.nq_event(None, None, 'played_this_card', message)
