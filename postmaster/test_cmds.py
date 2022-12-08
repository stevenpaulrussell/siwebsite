import time
import json

from django.test import TestCase

from filer import views as filerviews 
from . import cmds, saveget, postcards, connects




class TwiSim:
    def __init__(self, name):
        self.mobile = f'mobile_{name}'
        self.twilnumber0 = f'twil0_{name}'
        self.twilnumber1 = f'twil1_{name}'
        self.profile_url = f'profile_{name}'
        self.url_count = 0

    def _cmd_common(self, **message):
        message['sent_at'] = time.time()
        message['from_tel'] = self.mobile
        message['to_tel'] = self.twilnumber0
        return message

    def _make_wip(self):
        wip = dict(image_timestamp='image_timestamp', audio_timestamp='audio_timestamp')
        wip['image_url'] = f'image_url{self.url_count}'
        wip['audio_url'] = f'audio_url{self.url_count}'
        ++self.url_count
        return wip

    def _new_postcard_common(self):
        postcard_common = self._cmd_common()
        postcard_common['cmd'] = 'new_postcard'
        postcard_common['wip'] = self._make_wip()
        return postcard_common

    def newsender_firstpostcard(self):
        sqs_message = self._new_postcard_common()
        sqs_message['context'] = 'NewSenderFirst'
        sqs_message['profile_url'] = self.profile_url
        return json.dumps(sqs_message)

    def newrecipient_postcard(self):
        sqs_message = self._new_postcard_common()
        sqs_message['context'] = 'NewRecipientFirst'
        return json.dumps(sqs_message)

    def newpostcard_noviewer(self):
        sqs_message = self._new_postcard_common()
        sqs_message['context'] = 'NoViewer'
        return json.dumps(sqs_message)

    def newpostcard_haveviewer(self):
        sqs_message = self._new_postcard_common()
        sqs_message['context'] = 'HaveViewer'
        return json.dumps(sqs_message)

    
    def profile(self):
        return 'sqs dq sim'

    def set_from(self):
        return 'sqs dq sim'

    def set_to(self):
        return 'sqs dq sim'

    def connect(self):
        return 'sqs dq sim'

    def connector(self):
        return 'sqs dq sim'



class OneCmdTests(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = TwiSim(name='user1')
        self.User2 = TwiSim(name='user2')
        self.User3 = TwiSim(name='user3')

    def test_newsenderfirst(self):
        """ Test basic functioning using newsender_firstpostcard """
        Sender0 = TwiSim('Mr0')
        sqs_message = Sender0.newsender_firstpostcard()
        res = cmds.interpret_one_cmd(sqs_message)
        sender = saveget.get_sender(Sender0.mobile)
        self.assertEqual(sender['profile_url'], 'profile_Mr.0')

    def test_using_simulation_of_two_senders(self):
        Sender0 = TwiSim('Mr.0')
        Sender1 = TwiSim('Ms.1')
        # Twilio side is quiet until the sender succeeds in 'sign-up' by making wip and a profile.
        # Sender0 and Sender1 sign up, neither has a viewer yet. Nothing new being tested here
        res0 = cmds.interpret_one_cmd(Sender0.newsender_firstpostcard())
        res1 = cmds.interpret_one_cmd(Sender1.newsender_firstpostcard())
        # Sender1 sends to a second twilio number without establishing any viewer
        #    ????????? How to write this second to_tel  ?????
        # res1 = cmds.interpret_one_cmd(Sender0.newrecipient_postcard())
        sender1 = saveget.get_sender(Sender1.mobile)
        self.assertEqual(sender1['profile_url'], 'profile_Ms.1')
        self.assertFalse('I do not know how to write the second to_tel')






        

        


        
