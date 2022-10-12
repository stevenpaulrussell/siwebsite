import boto3
import json
import os

# Production read and write source is an AWS bucket.  
# Test read and write may be to a 'TEST bucket.

client = boto3.client(
            's3', 
            aws_access_key_id=os.environ['AWSAccessKeyId'], 
            aws_secret_access_key=os.environ['AWSSecretKey']
            )

if os.environ['TEST'] == 'True':    
    TEST = True
    aws_read_bucket_name = os.environ['TEST_BUCKET']        # This from .env  Not from Heroku config
    aws_write_bucket_name = os.environ['TEST_BUCKET']  
elif os.environ['TEST'] == 'Beta':
    TEST = 'Beta'
    aws_read_bucket_name = os.environ['BETA_BUCKET']        # From Heroku config
    aws_write_bucket_name = os.environ['BETA_BUCKET']  
else:
    TEST = False
    assert os.environ['TEST'] == 'False'
    aws_read_bucket_name = os.environ['ALPHA_BUCKET']       # From Heroku config
    aws_write_bucket_name = os.environ['ALPHA_BUCKET']


#loading
def load_one_sender_state(from_tel):
    return  _load_a_thing_using_key(f'sender/{from_tel}')

def load_one_po_box(pobox_id):
    return _load_a_thing_using_key(f'box/{pobox_id}')

def load_recently_played_card_list_from_s3():
    try:
        return _load_a_thing_using_key('Recently_Played_Cards_v1')
    except(Exception) as E:
        if TEST:            # If running Beta or Test, not an error.
            return {}
        else:
            raise

def load_recently_played_card_list_as_last_seen_from_s3():
    try:
        return _load_a_thing_using_key('Recently_Played_Cards_v1_as_last_seen')
    except(Exception) as E:
        return {}

def load_a_postcard_from_s3(postcard_uuid):
    return _load_a_thing_using_key(thing_key=f'card/{postcard_uuid}')

def load_all_senders():
    senders = {}
    s3_response = client.list_objects_v2(Bucket=aws_read_bucket_name, Prefix='sender/')
    if 'Contents' in s3_response:
        for object in s3_response['Contents']:
            sender = _load_a_thing_using_key(object["Key"])
            senders_key = sender['from_tel']
            senders[senders_key] = sender
    return senders

def load_all_po_boxes():
    post_office = {}
    s3_response = client.list_objects_v2(Bucket=aws_read_bucket_name, Prefix='box/')
    if 'Contents' in s3_response:
        for object in s3_response['Contents']:
            po_box = _load_a_thing_using_key(object["Key"])
            po_boxes_key = po_box['po_box_id']
            post_office[po_boxes_key] = po_box
    return post_office


# Saving
def save_one_sender_state(sender):
    _save_a_thing_using_key(sender, thing_key=f'sender/{sender["from_tel"]}')

def save_one_po_box(po_box):
    _save_a_thing_using_key(po_box, thing_key=f'box/{po_box["po_box_id"]}')

def save_senders_to_s3(senders):
    for from_tel in senders:
        save_one_sender_state(senders[from_tel])

def save_post_office_to_s3(post_office):
    for po_box_id in post_office:
        save_one_po_box(post_office[po_box_id])

def save_a_postcard_to_S3(postcard):
    _save_a_thing_using_key(thing=postcard, thing_key=f'card/{postcard["uuid"]}')

def save_recently_played_card_list_to_s3(recently_played):
    _save_a_thing_using_key(recently_played, 'Recently_Played_Cards_v1')

def save_recently_played_card_list_as_last_seen_to_s3(recently_played):
    _save_a_thing_using_key(recently_played, 'Recently_Played_Cards_v1_as_last_seen')

def delete_a_sender(sender):
    _delete_a_thing_using_key(thing_key=f'sender/{sender["from_tel"]}')


# Utility functions
def _load_a_thing_using_key(thing_key):
    response_dictionary = client.get_object(Bucket=aws_read_bucket_name, Key=thing_key)
    return json.loads(response_dictionary['Body'].read())

def _save_a_thing_using_key(thing, thing_key):
    if TEST and aws_write_bucket_name == os.environ['ALPHA_BUCKET']:    # Exception unless False
        raise ValueError('In pbox.filer, trying to write to the production bucket')
    datastring = json.dumps(thing)
    client.put_object(Body=datastring, Bucket=aws_write_bucket_name, Key=thing_key)

def _delete_a_thing_using_key(thing_key):
    client.delete_object(Bucket=aws_read_bucket_name, Key=thing_key)


def clear_the_read_bucket(PREFIX=''):
    if TEST != True:
        raise Exception('In filer, calling clear_the_read_bucket with TEST = {TEST}')
    else:
        s3_response = client.list_objects_v2(Bucket=aws_read_bucket_name, Prefix=PREFIX)
        if 'Contents' in s3_response:
            for object in s3_response['Contents']:
                client.delete_object(Bucket=aws_read_bucket_name, Key=object['Key'])


