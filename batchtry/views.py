

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

def load_state_from_s3():
    all_data = _load_a_thing_using_key('All_Data_Test_v1')
    if all_data:
        senders = all_data['senders']
        post_office = all_data['post_office']
        cards_in_progress = all_data['cards_in_progress']
        connections = all_data['connections']
        postal_admin = all_data['postal_admin']
        return senders, post_office, cards_in_progress, connections, postal_admin
    else:
        return {}, {}, {}, {}, {}

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
    return _load_a_thing_using_key(thing_key=f'cards/{postcard_uuid}')



# Utility functions
def _load_a_thing_using_key(thing_key):
    response_dictionary = client.get_object(Bucket=aws_read_bucket_name, Key=thing_key)
    return json.loads(response_dictionary['Body'].read())

def get_cards(limit=1000):
    all_cards = []
    count = 0
    result_dictionary = client.list_objects_v2(Bucket = aws_read_bucket_name, Prefix='cards/')
    for item in result_dictionary.get('Contents'):
        count += 1
        key = item.get('Key')
        card = _load_a_thing_using_key(key)
        all_cards.append(card)
        if count == limit:
            break
    return all_cards
