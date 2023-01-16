"""
S3 and SQS read and write functions localized here.
"""
import time
import json
import os

import boto3


# Placeholder for static file storing strings for constructing messages
ALL_MESSAGES = {}
legal_commands = 'help ? profile connector connect from: to:'
completed_onboarding_message = 'Welcome to the postcarding system! To set up a viewer for postcards, or to get other instructions, \
    please go to https://dry-sierra-55179.herokuapp.com/.'


MGMT_TELEPHONE_NUMBER = 'MGMT_TELEPHONE_NUMBER'
DEFAULT_TWILIO_NUMBER = '+18326626430'

#  twilio3-commands   or   twilio3-tests
CMD_SQS = 'twilio3-commands'
ADMIN_SQS = 'twilio3-admin'
TEST_CMD_SQS = 'twilio3-tests'
TEST_ADMIN_SQS = 'twilio3-admin_tests'


# Set up resources to access AWS
S3client = boto3.client(
            's3', 
            aws_access_key_id=os.environ['AWSAccessKeyId'], 
            aws_secret_access_key=os.environ['AWSSecretKey']
            )

SQSClient = boto3.client(
            'sqs', 
            region_name = 'us-east-1',
            aws_access_key_id=os.environ['AWSAccessKeyId'], 
            aws_secret_access_key=os.environ['AWSSecretKey']
            )

if os.environ['TEST'] == 'True':    
    TEST = True
    aws_bucket_name = os.environ['TEST_BUCKET']        # This from .env  Not from Heroku config
    CMD_SQS = TEST_CMD_SQS
    ADMIN_SQS = TEST_ADMIN_SQS
CMD_URL = SQSClient.get_queue_url(QueueName=CMD_SQS)['QueueUrl']
ADMIN_URL = SQSClient.get_queue_url(QueueName=ADMIN_SQS)['QueueUrl']
print('Remember to add the sqs names to .env filer.views line 33 or so')


class S3Error(Exception):
    pass
class S3KeyNotFound(S3Error):
    pass


# S3 Loading
def load_from_free_tier(from_tel):
    try:
        return  _load_a_thing_using_key(f'free_tier/{from_tel}')
    except S3KeyNotFound:
        return None

def load_from_new_sender(from_tel):
    try:
        return  _load_a_thing_using_key(f'new_sender/{from_tel}')
    except S3KeyNotFound:
        return None

def load_wip(from_tel, to_tel):
    try:
        return  _load_a_thing_using_key(f'wip/{from_tel}/{to_tel}')
    except S3KeyNotFound:
        return {}


# S3 Saving
def save_new_sender(from_tel, expect):
    _save_a_thing_using_key(thing=expect, key=f'new_sender/{from_tel}')

def update_free_tier(from_tel, to_tel, sender_name=None, recipient_name=None):  # 'from' seems to be a reserved keyword
    sender_name = sender_name or f'{from_tel[-4]} {from_tel[-3]} {from_tel[-2]} {from_tel[-1]}'
    recipient_name = recipient_name or 'a kith or kin'
    key = f'free_tier/{from_tel}'
    try:
        value = _load_a_thing_using_key(key)
    except S3KeyNotFound:
        value = {}
    value.update({to_tel: {'from': sender_name, 'to': recipient_name}})
    _save_a_thing_using_key(value, key)

def save_wip(from_tel, to_tel, wip):
    _save_a_thing_using_key(wip, key=f'wip/{from_tel}/{to_tel}')

def delete_wip(from_tel, to_tel):
    _delete_a_thing_using_key(key=f'wip/{from_tel}/{to_tel}')



# S3 Utility functions
def _load_a_thing_using_key(key):
    try:
        response_dictionary = S3client.get_object(Bucket=aws_bucket_name, Key=key)
    except S3client.exceptions.NoSuchKey:
        raise S3KeyNotFound
    return json.loads(response_dictionary['Body'].read())

def _save_a_thing_using_key(thing, key):
    datastring = json.dumps(thing)
    S3client.put_object(Body=datastring, Bucket=aws_bucket_name, Key=key)

def _delete_a_thing_using_key(key):
    S3client.delete_object(Bucket=aws_bucket_name, Key=key)

def clear_the_read_bucket(PREFIX=''):
    if TEST != True:
        raise Exception('In filer, calling clear_the_read_bucket with TEST = {TEST}')
    else:
        s3_response = S3client.list_objects_v2(Bucket=aws_bucket_name, Prefix=PREFIX)
        if 'Contents' in s3_response:
            for object in s3_response['Contents']:
                S3client.delete_object(Bucket=aws_bucket_name, Key=object['Key'])


# SQS Use Functions
def nq_cmd(from_tel, to_tel, cmd, **message):
    message.update(dict(from_tel=from_tel, to_tel=to_tel, cmd=cmd))
    send_an_sqs_message(message, CMD_URL)

def nq_admin_message(message):
    send_an_sqs_message(message, ADMIN_URL)

def nq_postcard(from_tel, to_tel, **message):
    """Build and sqs message, call filer to send it, call filer to remove the wip."""
    message['sent_at'] = time.time()
    nq_cmd(from_tel=from_tel, to_tel=to_tel, cmd='new_postcard',  **message)
    delete_wip(from_tel=from_tel, to_tel=to_tel)


# SQS Utility functions
def send_an_sqs_message(message, QueueUrl):
    json_message = json.dumps(message)
    SQSClient.send_message(MessageBody=json_message, QueueUrl=QueueUrl)

def get_an_sqs_message(QueueUrl=CMD_URL):
    response = SQSClient.receive_message(QueueUrl=QueueUrl, WaitTimeSeconds=1)
    if 'Messages' in response:
        sqs_message = response['Messages'][0]
        json_message = sqs_message['Body']
        receipt_handle = sqs_message['ReceiptHandle']
        SQSClient.delete_message(QueueUrl=QueueUrl, ReceiptHandle=receipt_handle)
        return json.loads(json_message)
    else:
        return None

def clear_the_sqs_queue_TEST_SQS(PREFIX=''):
    if TEST != True:
        raise Exception('In filer, calling clear_the_read_bucket with TEST = {TEST}')
    else:
        while True:
            message = get_an_sqs_message()
            if not message:
                break
        while True:
            message = get_an_sqs_message(QueueUrl=ADMIN_URL)
            if not message:
                break


