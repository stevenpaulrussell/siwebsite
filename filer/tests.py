"""
Tests of filer functions which include SQS for test harness.
"""

import json
import time

from django.test import TestCase

from .exceptions import S3KeyNotFound
from . import views 
from . import lines

# class FilerViewS3FunctionsWork(TestCase):
#     def setUp(self) -> None:
#         views.clear_the_read_bucket()
#         self.new_from_tel = '+12135551212'
#         self.new_to_tel = '+13105551212'

#     def test_missing_key_raises_exception_in____load_a_thing_using_key(self):
#         with self.assertRaises(S3KeyNotFound):
#             res = views._load_a_thing_using_key(self.new_from_tel)

#     def test_load_from_free_tier_returns_None_on_missing_key(self):
#         res = views.load_from_free_tier(self.new_from_tel)
#         self.assertEqual(res, None)
       
#     def test_load_from_new_sender_returns_image_on_missing_key(self):
#         res = views.load_from_new_sender(self.new_from_tel)
#         self.assertEqual(res, 'image')

#     def test_load_wip_returns_empty_dict_on_missing_key(self):
#         res = views.load_wip(self.new_from_tel, self.new_to_tel)
#         self.assertEqual(res, {})

#     def test__save_new_sender_works_fine(self):
#         views.save_new_sender(self.new_from_tel, expect='audio')
#         res = views.load_from_new_sender(self.new_from_tel)
#         self.assertEqual(res, 'audio')

#     def test__save_wip_works_fine(self):
#         test_wip = dict(image_timestamp='image_timestamp', image_url='image_url')
#         views.save_wip(self.new_from_tel, self.new_to_tel, test_wip)
#         res = views.load_wip(self.new_from_tel, self.new_to_tel)
#         self.assertEqual(res, test_wip)


class FilerViewSQS_Utility_FunctionsWork(TestCase):
    def setUp(self) -> None:
        # twilio3-postcards   or   twilio3-commands   or   twilio3-tests
        self.QUEUENAME = 'twilio3-tests'
        while True:
            message = views.get_an_sqs_message(self.QUEUENAME)
            if message:
                print(f'\nIn FilerViewSQS_Utility_FunctionsWork setUp, got an SQS message:\n{message}')
            else:
                break


    def test_can_write_and_read_to_a_queue(self):
        json_message = json.dumps({'mylabel': 'test_can_write_and_read_to_a_queue'})
        views.send_an_sqs_message(queue_name=self.QUEUENAME, message=json_message)
        message = views.get_an_sqs_message(self.QUEUENAME)
        message_content = json.loads(message)
        self.assertEqual(message_content['mylabel'], 'test_can_write_and_read_to_a_queue')

    def test_can_write_multiple_and_read_from_a_queue(self):
        json_message0 = json.dumps({'mylabel': 'mycontent0'})
        json_message1 = json.dumps({'mylabel': 'mycontent1'})
        views.send_an_sqs_message(queue_name=self.QUEUENAME, message=json_message0)
        views.send_an_sqs_message(queue_name=self.QUEUENAME, message=json_message1)
        message0 = views.get_an_sqs_message(self.QUEUENAME)
        message1 = views.get_an_sqs_message(self.QUEUENAME)
        message2 = views.get_an_sqs_message(self.QUEUENAME)
        message0_content = json.loads(message0)
        message1_content = json.loads(message1)
        self.assertEqual(message0_content['mylabel'], 'mycontent0')
        self.assertEqual(message1_content['mylabel'], 'mycontent1')
        self.assertEqual(message2, None)



# class SQS_NQ_Functions_Work(TestCase):
#     def setUp(self) -> None:
#         return super().setUp()

#     def test_nq_postcard(self):
#         pass


# class Can_Make_Needed_Strings_in_Lines(TestCase):
#     def test_lines_no_params(self):
#         res = lines.line('key')
#         self.assertEqual(res, "<key looked up> using {}")

#     def test_lines_with_params(self):
#         res = lines.line('key', recipient='recipient name', sender='sender_name')
#         self.assertEqual(res, "<key looked up> using {'recipient': 'recipient name', 'sender': 'sender_name'}")

