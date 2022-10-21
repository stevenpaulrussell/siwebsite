"""
S3 and SQS read and write functions localized here.
"""

import boto3
from botocore.exceptions import ClientError
import json
import os

from . import exceptions

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


#S3
# Loading
def free_tier_flag(from_tel):
    print('What actually gets returned below... how to strip out?')
    try:
        return  _load_a_thing_using_key('free_tier/{from_tel}')
    except exceptions.S3KeyNotFound:
        return None

def load_from_free_tier(from_tel):
    print('What actually gets returned below... how to strip out?')
    try:
        return  _load_a_thing_using_key('new_sender/{from_tel}')
    except exceptions.S3KeyNotFound:
        return 'image'


# load new_sender and make blank if not found

# Saving
# save wip 


# SQS
def get_queue_url(queue_name):
    response = SQSClient.get_queue_url(QueueName=queue_name)
    return response['QueueUrl']

def send_an_sqs_message(queue_name, message):
    SQSClient.send_message(QueueUrl=get_queue_url(queue_name), MessageBody=message)

def get_sqs_messages(queue_name):
    message_list = []
    QueueUrl = get_queue_url(queue_name)
    response = SQSClient.receive_message(QueueUrl=QueueUrl)
    sqs_message_list = response['Messages']
    for sqs_message in sqs_message_list:
        receipt_handle = sqs_message['ReceiptHandle']
        message_list.append(sqs_message['Body'])
        SQSClient.delete_message(QueueUrl=QueueUrl, ReceiptHandle=receipt_handle)
    return message_list



# S3 Utility functions
def _load_a_thing_using_key(thing_key):
    try:
        response_dictionary = S3client.get_object(Bucket=aws_bucket_name, Key=thing_key)
    except S3client.exceptions.NoSuchKey:
        raise exceptions.S3KeyNotFound
    return json.loads(response_dictionary['Body'].read())

def _save_a_thing_using_key(thing, thing_key):
    datastring = json.dumps(thing)
    S3client.put_object(Body=datastring, Bucket=aws_bucket_name, Key=thing_key)

def _delete_a_thing_using_key(thing_key):
    S3client.delete_object(Bucket=aws_bucket_name, Key=thing_key)


def clear_the_read_bucket(PREFIX=''):
    if TEST != True:
        raise Exception('In filer, calling clear_the_read_bucket with TEST = {TEST}')
    else:
        s3_response = S3client.list_objects_v2(Bucket=aws_bucket_name, Prefix=PREFIX)
        if 'Contents' in s3_response:
            for object in s3_response['Contents']:
                S3client.delete_object(Bucket=aws_bucket_name, Key=object['Key'])


