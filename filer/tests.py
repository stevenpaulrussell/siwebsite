"""
Tests of filer functions which include SQS for test harness.
"""

import json
import time

from django.test import TestCase

from .exceptions import S3KeyNotFound
from . import views 
from . import lines
from . import twilio_cmds


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


# class FilerViewSQS_Utility_FunctionsWork(TestCase):
#     def setUp(self) -> None:
#         while True:
#             message = views.get_an_sqs_message()
#             if not message:
#                 break

#     def test_can_write_and_read_to_a_queue(self):
#         sent_message = {'mylabel': 'test_can_write_and_read_to_a_queue'}
#         views.send_an_sqs_message(message=sent_message, QueueUrl=views.CMD_URL)
#         received_message = views.get_an_sqs_message()
#         self.assertEqual(received_message['mylabel'], 'test_can_write_and_read_to_a_queue')

#     def test_can_write_multiple_and_read_from_a_queue(self):
#         sent_message0 = {'mylabel': 'mycontent0'}
#         sent_message1 = {'mylabel': 'mycontent1'}
#         views.send_an_sqs_message(message=sent_message0, QueueUrl=views.CMD_URL)
#         views.send_an_sqs_message(message=sent_message1, QueueUrl=views.CMD_URL)
#         received_message0 = views.get_an_sqs_message()
#         received_message1 = views.get_an_sqs_message()
#         received_message2 = views.get_an_sqs_message()

#         # FIFO not guaranteed, but per-sender processing written so few second FIFO not needed
#         self.assertIn(received_message0['mylabel'], ('mycontent0', 'mycontent1'))
#         self.assertIn(received_message1['mylabel'], ('mycontent0', 'mycontent1'))
#         self.assertEqual(received_message2, None)



# class NQ_Functions_Put_Content_In_SQS(TestCase):
#     def setUp(self) -> None:
#         self.from_tel = '+12135551212'
#         self.to_tel = '+13105551212'
#         self.url1 = 'url1'
#         self.url2 = 'url2'

#     def test_nq_postcard(self):
#         now = time.time()
#         wip =  dict(image_timestamp=now, image_url=self.url1, audio_timestamp=now, audio_url=self.url2)
#         views.save_wip(self.from_tel, self.to_tel, wip)               
#         S3_wip_before = views.load_wip(self.from_tel, self.to_tel)
#         # call to nq_postcard writes to sqs and deletes wip from S3
#         views.nq_postcard(self.from_tel, self.to_tel, wip)
#         S3_wip_after = views.load_wip(self.from_tel, self.to_tel)
#         postcard_message = views.get_an_sqs_message()
#         self.assertIn('from_tel', postcard_message)
#         self.assertIn('to_tel', postcard_message)
#         self.assertEqual(S3_wip_after, {})
#         self.assertEqual(postcard_message['wip'], wip)




class Can_Make_Needed_Strings_in_Lines(TestCase):
    def test_lines_no_params(self):
        res = lines.line('key')
        self.assertEqual(res, "<key looked up> using {}")

    def test_lines_with_params(self):
        res = lines.line('key', recipient='recipient name', sender='sender_name')
        self.assertEqual(res, "<key looked up> using {'recipient': 'recipient name', 'sender': 'sender_name'}")



class Twilio_Cmds_Testing(TestCase):
    def test_sms_to_some_telephone_number(self):
        # no_res = twilio_cmds.sms_to_some_telephone_number('Test filer line 116', 
        #         '+16502196500', twilio_number=views.DEFAULT_TWILIO_NUMBER)
        # print(f'\n\nFinished test, got no_res: {no_res}\n\n')
        # self.assertEqual(no_res, None)
        self.assertFalse('Took this working test, and rewrote to test sms_back and sms_mgmt_message.')

    def test_have_given_Http_return_to_each_twilio_call(self):
        self.assertFalse('Still have to check the twilio HTTP returns.')
