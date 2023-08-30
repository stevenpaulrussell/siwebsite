"""
Tests of filer functions which include SQS for test harness.
"""

import json
import time

from django.test import TestCase

from . import views 
from . import lines
from . import twilio_cmds


class FilerViewS3FunctionsWork(TestCase):
    def setUp(self) -> None:
        views.clear_the_read_bucket()
        self.new_tel_id = '+12135551212'
        self.new_svc_id = '+13105551212'

    def test_missing_key_raises_exception_in____load_a_thing_using_key(self):
        with self.assertRaises(views.S3KeyNotFound):
            res = views._load_a_thing_using_key(self.new_tel_id)

    def test_load_from_free_tier_returns_None_on_missing_key(self):
        res = views.load_from_free_tier(self.new_tel_id)
        self.assertEqual(res, None)

    def test__update_free_tier_works_to_initiate(self):
        views.update_free_tier(tel_id=self.new_tel_id, svc_id=self.new_svc_id)
        res = views.load_from_free_tier(self.new_tel_id)
        self.assertIsInstance(res, dict)
        self.assertEqual(res[self.new_svc_id]['from'], '1 2 1 2')
        self.assertEqual(res[self.new_svc_id]['to'], 'a kith or kin')
       
    def test_load_from_new_sender_returns_image_on_missing_key(self):
        res = views.load_from_new_sender(self.new_tel_id)
        self.assertIsNone(res)

    def test_load_wip_returns_empty_dict_on_missing_key(self):
        res = views.load_wip(self.new_tel_id, self.new_svc_id)
        self.assertEqual(res, {})

    def test__save_new_sender_works_fine(self):
        views.save_new_sender(self.new_tel_id, expect='audio')
        res = views.load_from_new_sender(self.new_tel_id)
        self.assertEqual(res, 'audio')

    def test__save_wip_works_fine(self):
        test_wip = dict(image_timestamp='image_timestamp', image_url='image_url')
        views.save_wip(self.new_tel_id, self.new_svc_id, test_wip)
        res = views.load_wip(self.new_tel_id, self.new_svc_id)
        self.assertEqual(res, test_wip)



class FilerViewSQS_Utility_FunctionsWork(TestCase):
    def setUp(self) -> None:
        views.clear_the_sqs_queue_TEST_SQS()

    def test_can_write_and_read_to_a_queue(self):
        sent_message = {'mylabel': 'test_can_write_and_read_to_a_queue'}
        views.send_an_sqs_message(message=sent_message, QueueUrl=views.EVENT_URL)
        received_message = views.get_an_sqs_message()
        self.assertEqual(received_message['mylabel'], 'test_can_write_and_read_to_a_queue')

    def test_can_write_multiple_and_read_from_a_queue(self):
        sent_message0 = {'mylabel': 'mycontent0'}
        sent_message1 = {'mylabel': 'mycontent1'}
        views.send_an_sqs_message(message=sent_message0, QueueUrl=views.EVENT_URL)
        views.send_an_sqs_message(message=sent_message1, QueueUrl=views.EVENT_URL)
        received_message0 = views.get_an_sqs_message()
        received_message1 = views.get_an_sqs_message()
        received_message2 = views.get_an_sqs_message()

        # FIFO not guaranteed, but per-sender processing written so few second FIFO not needed
        self.assertIn(received_message0['mylabel'], ('mycontent0', 'mycontent1'))
        self.assertIn(received_message1['mylabel'], ('mycontent0', 'mycontent1'))
        self.assertEqual(received_message2, None)


class NQ_Functions_Put_Content_In_SQS(TestCase):
    def setUp(self) -> None:
        self.tel_id = '+12135551212'
        self.svc_id = '+13105551212'
        self.url1 = 'url1'
        self.url2 = 'url2'

    def test_nq_postcard(self):
        now = time.time()
        wip =  dict(image_timestamp=now, image_url=self.url1, audio_timestamp=now, audio_url=self.url2)
        views.save_wip(self.tel_id, self.svc_id, wip)               
        S3_wip_before = views.load_wip(self.tel_id, self.svc_id)
        # call to nq_postcard writes to sqs and deletes wip from S3
        views.nq_postcard(self.tel_id, self.svc_id, wip=wip, context='HaveViewer')
        S3_wip_after = views.load_wip(self.tel_id, self.svc_id)
        postcard_message = views.get_an_sqs_message()
        self.assertIn('tel_id', postcard_message)
        self.assertIn('svc_id', postcard_message)
        self.assertIn('context', postcard_message)
        self.assertIn('sent_at', postcard_message)
        self.assertEqual(S3_wip_after, {})
        self.assertEqual(postcard_message['wip'], wip)


class Can_Make_Needed_Strings_in_Lines(TestCase):
    def test_lines_no_params(self):
        msg_key = 'msg_key_no_variables'
        res = lines.line(msg_key)
        self.assertEqual(res, 'msg_key_no_variables')

    def test_lines_with_params(self):
        msg_key = 'msg_key_{name}_{value}'
        keys = dict(name='fulano', value=76)
        res = lines.line(msg_key, **keys)
        self.assertEqual(res, 'msg_key_fulano_76')

    def test_lines_with_extra_params(self):
        msg_key = 'msg_key_{name}_{value}'
        keys = dict(name='fulano', value=76, xtra1=1, xtra2=2)
        res = lines.line(msg_key, **keys)
        self.assertEqual(res, 'msg_key_fulano_76')



class Twilio_Cmds_Testing(TestCase):
    def setUp(self) -> None:
        self.tel_id = '+12135551212'
        self.svc_id = '+13105551212'
        
    def xtest_sms_to_some_telephone_number(self):
        """This test does an actual sms send using twilio, so it is marked as 'xtest_... to not run."""
        no_res = twilio_cmds.sms_to_some_telephone_number('Test filer line 116', 
                '+16502196500', twilio_number=views.DEFAULT_TWILIO_NUMBER)
        print(f'\n\nFinished test, got no_res: {no_res}\n\n')
        self.assertEqual(no_res, None)

    def test_sms_back_in_TEST_env_queues_msg_to_TEST_SQS_aka_twilio3tests(self):
        message_key = 'testing sms back'
        keys = dict(keysize='just one key')
        no_res = twilio_cmds.sms_back(self.tel_id, self.svc_id, message_key, **keys)
        queued_sms_msg = views.get_an_sqs_message(views.ADMIN_URL)
        self.assertIsInstance(queued_sms_msg, dict)
        self.assertEqual(queued_sms_msg['message_key'], message_key)
        self.assertIsInstance(queued_sms_msg['kwds'], dict)
        self.assertEqual(queued_sms_msg['kwds']['keysize'], 'just one key')
