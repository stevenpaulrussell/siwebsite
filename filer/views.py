"""
S3 and SQS read and write functions localized here.
"""

import boto3
from botocore.exceptions import ClientError
import json
import os

from . import exceptions

# twilio3-postcards   or   twilio3-commands   or   twilio3-tests
POSTCARD_SQS = 'twilio3-postcards'
CMD_SQS = 'twilio3-commands'
TEST_SQS = 'twilio3-tests'

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


# S3 Loading
def load_from_free_tier(from_tel):
    try:
        return  _load_a_thing_using_key('free_tier/{from_tel}')
    except exceptions.S3KeyNotFound:
        return None

def load_from_new_sender(from_tel):
    try:
        return  _load_a_thing_using_key(f'new_sender/{from_tel}')
    except exceptions.S3KeyNotFound:
        return 'image'

def load_wip(from_tel, to_tel):
    try:
        return  _load_a_thing_using_key(f'wip/{from_tel}/{to_tel}')
    except exceptions.S3KeyNotFound:
        return {}


# S3 Saving
def save_new_sender(from_tel, expect):
    _save_a_thing_using_key(thing=expect, key=f'new_sender/{from_tel}')

def save_wip(from_tel, to_tel, wip):
    _save_a_thing_using_key(wip, key=f'wip/{from_tel}/{to_tel}')

def delete_wip(from_tel, to_tel):
    _delete_a_thing_using_key(key=f'wip/{from_tel}/{to_tel}')



# S3 Utility functions
def _load_a_thing_using_key(key):
    try:
        response_dictionary = S3client.get_object(Bucket=aws_bucket_name, Key=key)
    except S3client.exceptions.NoSuchKey:
        raise exceptions.S3KeyNotFound
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
def nq_postcard(from_tel, to_tel, wip):
    """Build and sqs message, call filer to send it, call filer to remove the wip."""
    message = dict(from_tel=from_tel, to_tel=to_tel, wip=wip, version=1)
    send_an_sqs_message(POSTCARD_SQS, message)
    delete_wip(from_tel=from_tel, to_tel=to_tel)

def nq_cmd(from_tel, cmd_json):
        """Call filer to send it."""

def nq_admin_message(message):
        """Call filer to send it."""

# SQS Utility functions
def get_queue_url(queue_name):
    response = SQSClient.get_queue_url(QueueName=queue_name)
    return response['QueueUrl']

def send_an_sqs_message(queue_name, message):
    json_message = json.dumps(message)
    SQSClient.send_message(QueueUrl=get_queue_url(queue_name), MessageBody=json_message)

def get_an_sqs_message(queue_name):
    QueueUrl = get_queue_url(queue_name)
    response = SQSClient.receive_message(QueueUrl=QueueUrl, WaitTimeSeconds=1)
    if 'Messages' in response:
        sqs_message = response['Messages'][0]
        json_message = sqs_message['Body']
        receipt_handle = sqs_message['ReceiptHandle']
        SQSClient.delete_message(QueueUrl=QueueUrl, ReceiptHandle=receipt_handle)
        return json.loads(json_message)
    else:
        return None

