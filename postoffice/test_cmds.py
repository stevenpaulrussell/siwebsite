import time
import uuid
import pprint


from django.test import TestCase

from siwebsite_project.test_functional import TwiSim
from filer import views as filerviews 
from saveget import saveget

from . import cmds, postcards, connects

class OneCmdTests(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()

    def test_newsenderfirst(self):
        """ Test basic functioning using newsender_firstpostcard """
        Sender0 = TwiSim('Mr0')
        sqs_message = Sender0.newsender_firstpostcard()
        cmds.interpret_one_cmd(sqs_message)
        sender = saveget.get_sender(Sender0.mobile)
        self.assertEqual(sender['profile_url'], 'profile_Mr0')

    def test__dq_and_do_one_cmd(self):
        Sender0 = TwiSim('Mr0')
        sqs_message = Sender0.newsender_firstpostcard()
        saveget._test_send_an_sqs_event(sqs_message)
        cmds.dq_and_do_one_cmd()
        sender = saveget.get_sender(Sender0.mobile)
        self.assertEqual(sender['profile_url'], 'profile_Mr0')
       
