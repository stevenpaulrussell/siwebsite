"""
Tests of filer functions which include SQS for test harness.
"""

import json

from django.test import TestCase

from .exceptions import S3KeyNotFound
from . import views 

class FilerViewS3FunctionsWork(TestCase):
    def setUp(self) -> None:
        views.clear_the_read_bucket()
        self.newphonenumber = '+12135551212'

    def test_missing_key_raises_exception_in____load_a_thing_using_key(self):
        with self.assertRaises(S3KeyNotFound):
            res = views._load_a_thing_using_key(self.newphonenumber)

    def test_load_twitalk_freetier_raises_exception_on_missing_key(self):
        with self.assertRaises(S3KeyNotFound):
            res = views.load_twitalk_freetier(self.newphonenumber)
       
    def test_load_new_sender_raises_exception_on_missing_key(self):
        with self.assertRaises(S3KeyNotFound):
            res = views.load_new_sender(self.newphonenumber)
       
    def test_can_save_new_sender_and_read_it(self):
        views.save_new_sender_state(self.newphonenumber, {'greet': 'hi there'})
        res = views.load_new_sender(self.newphonenumber)
        self.assertEqual(res['greet'], 'hi there')

class FilerViewSQS_FunctionsWork(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_can_find_a_queue(self):
        # twilio3-postcards   or   twilio3-commands   or   twilio3-tests
        queue_name = 'twilio3-commands'   
        url = views.get_queue_url(queue_name)
        self.assertTrue(queue_name in url)

    def test_can_write_and_read_to_a_queue(self):
        json_message = json.dumps({'mylabel': 'mycontent'})
        views.send_an_sqs_message(queue_name='twilio3-commands', message=json_message)
        message_list = views.get_sqs_messages('twilio3-commands')
        message = json.loads(message_list[0])
        print(message)
        self.assertEqual(len(message_list), 1)
        self.assertEqual(message['mylabel'], 'mycontent')


       


