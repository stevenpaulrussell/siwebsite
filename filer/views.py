import boto3
from botocore.exceptions import ClientError
import json
import os

from . import exceptions

client = boto3.client(
            's3', 
            aws_access_key_id=os.environ['AWSAccessKeyId'], 
            aws_secret_access_key=os.environ['AWSSecretKey']
            )

if os.environ['TEST'] == 'True':    
    TEST = True
    aws_bucket_name = os.environ['TEST_BUCKET']        # This from .env  Not from Heroku config


#loading
def load_twitalk_freetier(from_tel):
    key = f'free_tier/{from_tel}'
    return  _load_a_thing_using_key(f'free_tier/{from_tel}')

def load_new_sender(from_tel):
    key = f'new_sender/{from_tel}'
    return  _load_a_thing_using_key(f'new_sender/{from_tel}')

# Saving
def save_new_sender_state(from_tel, state):
    _save_a_thing_using_key(state, thing_key=f'new_sender/{from_tel}')




# Utility functions
def _load_a_thing_using_key(thing_key):
    try:
        response_dictionary = client.get_object(Bucket=aws_bucket_name, Key=thing_key)
    except client.exceptions.NoSuchKey:
        raise exceptions.S3KeyNotFound
    return json.loads(response_dictionary['Body'].read())

def _save_a_thing_using_key(thing, thing_key):
    datastring = json.dumps(thing)
    client.put_object(Body=datastring, Bucket=aws_bucket_name, Key=thing_key)

def _delete_a_thing_using_key(thing_key):
    client.delete_object(Bucket=aws_bucket_name, Key=thing_key)


def clear_the_read_bucket(PREFIX=''):
    if TEST != True:
        raise Exception('In filer, calling clear_the_read_bucket with TEST = {TEST}')
    else:
        s3_response = client.list_objects_v2(Bucket=aws_bucket_name, Prefix=PREFIX)
        if 'Contents' in s3_response:
            for object in s3_response['Contents']:
                client.delete_object(Bucket=aws_bucket_name, Key=object['Key'])


