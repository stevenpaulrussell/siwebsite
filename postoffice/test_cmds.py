import time
import uuid
import pprint


from django.test import TestCase

from siwebsite_project.test_functional import TwiSim
from filer import views as filerviews 
from saveget import saveget

from . import event_handler, postcards, connects

# class OneCmdTests(TestCase):
#     def setUp(self) -> None:
#         filerviews.clear_the_read_bucket()
#         filerviews.clear_the_sqs_queue_TEST_SQS()

#     def test_newsenderfirst(self):
#         """ Test basic functioning using newsender_firstpostcard """
#         Sender0 = TwiSim('Mr0')
#         sqs_message = Sender0.newsender_firstpostcard()
#         event_handler.interpret_one_event(sqs_message)
#         sender = saveget.get_sender(Sender0.mobile)
#         self.assertEqual(sender['profile_url'], 'profile_Mr0')

#     def test__dq_and_do_one_cmd(self):
#         Sender0 = TwiSim('Mr0')
#         sqs_message = Sender0.newsender_firstpostcard()
#         saveget._test_send_an_sqs_event(sqs_message)
#         event = saveget.get_one_sqs_event()
#         event_handler.interpret_one_event(event)
#         sender = saveget.get_sender(Sender0.mobile)
#         self.assertEqual(sender['profile_url'], 'profile_Mr0')
       
