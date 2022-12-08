import time
import json

from django.test import TestCase

from filer import views as filerviews 
from . import cmds, saveget, postcards, connects




class TwiSim:
    def __init__(self, name):
        self.mobile = f'mobile_{name}'
        self.twi_directory = dict(twilnumber0=f'twil0_{name}', twilnumber1=f'twil1_{name}')
        self.profile_url = f'profile_{name}'
        self.url_count = 0

    def _cmd_common(self, twinumber, **message):
        message['sent_at'] = time.time()
        message['from_tel'] = self.mobile
        message['to_tel'] = self.twi_directory[twinumber]
        return message

    def _make_wip(self):
        wip = dict(image_timestamp='image_timestamp', audio_timestamp='audio_timestamp')
        wip['image_url'] = f'image_url{self.url_count}'
        wip['audio_url'] = f'audio_url{self.url_count}'
        ++self.url_count
        return wip

    def _new_postcard_common(self, twinumber):
        postcard_common = self._cmd_common(twinumber)
        postcard_common['cmd'] = 'new_postcard'
        postcard_common['wip'] = self._make_wip()
        return postcard_common

    def newsender_firstpostcard(self, twinumber='twilnumber0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'NewSenderFirst'
        sqs_message['profile_url'] = self.profile_url
        return json.dumps(sqs_message)

    def newrecipient_postcard(self, twinumber='twilnumber0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'NewRecipientFirst'
        return json.dumps(sqs_message)

    def newpostcard_noviewer(self, twinumber='twilnumber0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'NoViewer'
        return json.dumps(sqs_message)

    def newpostcard_haveviewer(self, twinumber='twilnumber0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'HaveViewer'
        return json.dumps(sqs_message)

    
    def profile(self):
        return 'sqs dq sim'

    def set_from(self):
        return 'sqs dq sim'

    def set_to(self):
        return 'sqs dq sim'

    def connect(self):
        sqs_message = self._cmd_common(to_tel)
        sqs_message['cmd'] = 'cmd_general'
        sqs_message['text'] = 'connector'
        return json.dumps(sqs_message)

    def connector(self, to_tel):
        sqs_message = self._cmd_common(to_tel)
        sqs_message['cmd'] = 'cmd_general'
        sqs_message['text'] = 'connector'
        return json.dumps(sqs_message)



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
        self.assertEqual(sender['profile_url'], 'profile_Mr0')

    def test_using_simulation_of_two_senders(self):
        Sender0 = TwiSim('Mr0')
        Sender1 = TwiSim('Ms1')
        # Twilio side is quiet until the sender succeeds in 'sign-up' by making wip and a profile.
        # Sender0 and Sender1 sign up, neither has a viewer yet. Nothing new being tested here
        res0 = cmds.interpret_one_cmd(Sender0.newsender_firstpostcard())
        res1 = cmds.interpret_one_cmd(Sender1.newsender_firstpostcard())
        # Sender1 sends to a second twilio number without establishing any viewer
        res2 = cmds.interpret_one_cmd(Sender1.newrecipient_postcard('twilnumber1'))
        # Sender1 now sends a second card to the first twilio number
        res3 = cmds.interpret_one_cmd(Sender1.newpostcard_noviewer('twilnumber0'))
        # Check that all is as expected
        sender1_twilnumber0 = Sender1.twi_directory['twilnumber0']
        sender1_twilnumber1 = Sender1.twi_directory['twilnumber1']
        sender1 = saveget.get_sender(Sender1.mobile)
        self.assertEqual(sender1['profile_url'], 'profile_Ms1')
        self.assertIsNone(sender1['conn'][sender1_twilnumber0]['pobox_id'])
        self.assertIn(sender1_twilnumber1, sender1['conn'])
        a_card_id = sender1['conn'][sender1_twilnumber0]['recent_card_id']
        a_card = saveget.get_postcard(a_card_id)
        self.assertEqual(a_card['from_tel'], Sender1.mobile)

        # Sender0 makes a viewer.  This sets up the viewer data structure and returns the pobox_id
        # Check that, and see that pobox_id is retrieved on a re-look, and that bad values give None
        sender0 = saveget.get_sender(Sender0.mobile)
        sender0_twilnumber0 = Sender0.twi_directory['twilnumber0']
        pobox_id = connects.connect_viewer(sender0, sender0_twilnumber0)
        pobox_id_again = connects.connect_viewer(sender0, sender0_twilnumber0)
        res6 = connects.connect_viewer(sender0, 'some wrong twilio number')
        self.assertEqual(pobox_id, pobox_id_again)
        self.assertIsNone(res6)
        viewer_data = saveget.get_viewer_data(pobox_id)
        self.assertIn(Sender0.mobile, viewer_data)

        # Sender0 connects Sender1 to the viewer
        # First make the connector, checking msg back
        sender1_connector_msg_back = cmds.interpret_one_cmd(Sender1.connector('twilnumber0'))
        sender1_connector, to_tel_used = connects.get_passkey(Sender1.mobile)
        self.assertIn(sender1_connector, sender1_connector_msg_back)
        self.assertEqual(to_tel_used, Sender1.twi_directory['twilnumber0'])
        # Next issue the connect command and check results
        #sender0_connector_msg_back = cmds.interpret_one_cmd(Sender0.connect('twilnumber0'))
    



        # Sender1 sets up a to: name for a first recipient
        # Sender1 sets up a from: name for a first recipient







        

        


        
