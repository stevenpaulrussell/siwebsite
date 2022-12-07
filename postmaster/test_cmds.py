import time
import json

from django.test import TestCase

from filer import views as filerviews 
from . import cmds




class TwiSim:
    def __init__(self, name):
        self.mobile = f'mobile_{name}'
        self.twilnumber1 = 'twilnumber1'
        self.profile_url = f'profile)_{name}'
        self.url_count = 0

    def _nq_cmd(self, cmd, **message):
        message['sent_at'] = time.time()
        message['from_tel'] = self.mobile
        message['to_tel'] = self.twilnumber1
        message['cmd'] = cmd
        return message

    def make_wip(self):
        wip = dict(image_timestamp='image_timestamp', audio_timestamp='audio_timestamp')
        wip['image_url'] = f'image_url{self.url_count}'
        wip['audio_url'] = f'audio_url{self.url_count}'
        ++self.url_count
        return wip

    def NewSenderFirst(self):
        cmd = 'new_postcard'
        message = self._nq_cmd(cmd, context='NewSenderFirst', wip=self.make_wip(), profile_url=self.profile_url)
        return json.dumps(message)

    
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
        sender0 = TwiSim('Mr0')
        sqs_message = sender0.NewSenderFirst()
        print(f'debug in test line 66')
        res = cmds.interpret_one_cmd(sqs_message)
        self.assertIsNone(res)
        


        
