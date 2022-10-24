"""
Tests of filer functions which include SQS for test harness.
"""

import json

from django.test import TestCase

from .exceptions import S3KeyNotFound
from . import views 
from . import lines

class FilerViewS3FunctionsWork(TestCase):
    def setUp(self) -> None:
        views.clear_the_read_bucket()
        self.new_from_tel = '+12135551212'
        self.new_to_tel = '+13105551212'

    def test_missing_key_raises_exception_in____load_a_thing_using_key(self):
        with self.assertRaises(S3KeyNotFound):
            res = views._load_a_thing_using_key(self.new_from_tel)

    def test_load_from_free_tier_returns_None_on_missing_key(self):
        res = views.load_from_free_tier(self.new_from_tel)
        self.assertEqual(res, None)
       
    def test_load_from_new_sender_returns_image_on_missing_key(self):
        res = views.load_from_new_sender(self.new_from_tel)
        self.assertEqual(res, 'image')

    def test_load_wip_returns_empty_dict_on_missing_key(self):
        res = views.load_wip(self.new_from_tel, self.new_to_tel)
        self.assertEqual(res, {})

    def test__save_new_sender_works_fine(self):
        views.save_new_sender(self.new_from_tel, expect='audio')
        res = views.load_from_new_sender(self.new_from_tel)
        self.assertEqual(res, 'audio')

    def test__save_wip_works_fine(self):
        test_wip = dict(image_timestamp='image_timestamp', image_url='image_url')
        views.save_wip(self.new_from_tel, self.new_to_tel, test_wip)
        res = views.load_wip(self.new_from_tel, self.new_to_tel)
        self.assertEqual(res, test_wip)


class FilerViewSQS_Utility_FunctionsWork(TestCase):
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
        self.assertEqual(len(message_list), 1)
        self.assertEqual(message['mylabel'], 'mycontent')


class SQS_NQ_Functions_Work(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_nq_postcard(self):
        pass


class Can_Make_Needed_Strings_in_Lines(TestCase):
    def test_lines_no_params(self):
        res = lines.line('key')
        self.assertEqual(res, "<key looked up> using {}")

    def test_lines_with_params(self):
        res = lines.line('key', recipient='recipient name', sender='sender_name')
        self.assertEqual(res, "<key looked up> using {'recipient': 'recipient name', 'sender': 'sender_name'}")

