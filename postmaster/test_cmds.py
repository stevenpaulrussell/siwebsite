import time
import uuid
import json
import pprint


from django.test import TestCase

from filer import views as filerviews 
from . import cmds, saveget, postcards, connects




class TwiSim:
    def __init__(self, name):
        self.mobile = f'mobile_{name}'
        self.twi_directory = dict(twil0=f'twil0_{name}', twil1=f'twil1_{name}')
        self.profile_url = f'profile_{name}'
        self.url_count = 0

    def _cmd_common(self, twinumber, **message):
        message['cmd'] = 'cmd_general'
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

    def newsender_firstpostcard(self, twinumber='twil0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'NewSenderFirst'
        sqs_message['profile_url'] = self.profile_url
        return json.dumps(sqs_message)

    def newrecipient_postcard(self, twinumber='twil0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'NewRecipientFirst'
        return json.dumps(sqs_message)

    def newpostcard_noviewer(self, twinumber='twil0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'NoViewer'
        return json.dumps(sqs_message)

    def newpostcard_haveviewer(self, twinumber='twil0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'HaveViewer'
        return json.dumps(sqs_message)

    
    def set_profile(self, twinumber, profile_url):
        sqs_message = self._cmd_common(twinumber)
        sqs_message['cmd'] = 'profile'
        sqs_message['profile_url'] = profile_url
        return json.dumps(sqs_message)

    def set_from(self, twinumber, some_name):
        sqs_message = self._cmd_common(twinumber)
        sqs_message['text'] = f'from: {some_name}'
        return json.dumps(sqs_message)

    def set_to(self, twinumber, some_name):
        sqs_message = self._cmd_common(twinumber)
        sqs_message['text'] = f'to: {some_name}'
        return json.dumps(sqs_message)

    def connector(self, twinumber):
        sqs_message = self._cmd_common(twinumber)
        sqs_message['cmd'] = 'connector'
        sqs_message['passkey'] = str(uuid.uuid4())[0:4]
        sqs_message['expire'] = time.time() + 24*60*60
        return json.dumps(sqs_message)

    def connect(self, twilnumber, requestor_from_tel, passkey):
        sqs_message = self._cmd_common(twilnumber)
        sqs_message['text'] = f'connect {requestor_from_tel} connector {passkey}'
        return json.dumps(sqs_message)

pp = pprint.PrettyPrinter(indent=2)

def display_sender(from_tel, comment=None):
    if comment:
        print('\n\n','='*20)
        print(comment)
    sender = saveget.get_sender(from_tel)
    morsel = filerviews.load_from_free_tier(from_tel)
    print(f'\nsender <{from_tel}>:')
    pp.pprint(sender)
    print(f'\nmorsel <{from_tel}>:')
    pp.pprint(morsel)

def display_postal(pobox_id, comment=None):
    if comment:
        print('\n\n','='*20)
        print(comment)
    pobox = saveget.get_pobox(pobox_id)
    viewer_data = saveget.get_viewer_data(pobox_id)
    print(f'\npobox <{pobox_id}>:')
    pp.pprint(pobox)
    print(f'\nviewer_data <{pobox_id}>:')
    pp.pprint(viewer_data)

def display_postcard(card_id, comment=None):
    if comment:
        print('\n\n','='*20)
        print(comment)
    postcard = saveget.get_postcard(card_id)
    print(f'\npostcard <{card_id}>:')
    pp.pprint(postcard)


class OneCmdTests(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = TwiSim(name='user1')
        self.User2 = TwiSim(name='user2')
        self.User3 = TwiSim(name='user3')

    # def test_newsenderfirst(self):
    #     """ Test basic functioning using newsender_firstpostcard """
    #     Sender0 = TwiSim('Mr0')
    #     sqs_message = Sender0.newsender_firstpostcard()
    #     res = cmds.interpret_one_cmd(sqs_message)
    #     sender = saveget.get_sender(Sender0.mobile)
    #     self.assertEqual(sender['profile_url'], 'profile_Mr0')

    def test_using_simulation_of_two_senders(self):
        # Remember useful constants
        Sender0 = TwiSim('Mr0')
        Sender1 = TwiSim('Ms1')
        sender1_twil0 = Sender1.twi_directory['twil0']
        sender1_twil1 = Sender1.twi_directory['twil1']
        sender0_twil0 = Sender0.twi_directory['twil0']

        # Twilio side is quiet until the sender succeeds in 'sign-up' by making wip and a profile.
        # Sender0 and Sender1 sign up, neither has a viewer yet. Nothing new being tested here
        cmds.interpret_one_cmd(Sender0.newsender_firstpostcard())
        cmds.interpret_one_cmd(Sender1.newsender_firstpostcard())
        # Sender1 sends to a second twilio number
        cmds.interpret_one_cmd(Sender1.newrecipient_postcard('twil1'))
        # Sender1 sends a second card to the first twilio number
        cmds.interpret_one_cmd(Sender1.newpostcard_noviewer('twil0'))
        sender0 = saveget.get_sender(Sender0.mobile)
        sender1 = saveget.get_sender(Sender1.mobile)
        sender0_first_card_id = sender0['conn'][sender0_twil0]['recent_card_id']

        # Check that all is as expected
        self.assertEqual(sender1['profile_url'], 'profile_Ms1')
        self.assertIsNone(sender1['conn'][sender1_twil0]['pobox_id'])
        self.assertIsNone(sender1['conn'][sender1_twil1]['pobox_id'])
        sender1_card_id = sender1['conn'][sender1_twil0]['recent_card_id']
        sender1_card = saveget.get_postcard(sender1_card_id)
        self.assertEqual(sender1_card['from_tel'], Sender1.mobile)
        display_sender(Sender0.mobile, 'sender0 before setting any viewer')
        display_sender(Sender1.mobile, 'sender1, two recipients, before setting any viewer')

        # Sender0 makes a viewer.  This sets up the pobox, the viewer_data, putting a card in viewer_data, returning pobox_id
        # Check that, and see that pobox_id is retrieved on a re-look, and that bad values give None
        sender0 = saveget.get_sender(Sender0.mobile)
        pobox_id       = connects.connect_viewer(sender0, sender0_twil0)
        pobox_id_again = connects.connect_viewer(sender0, sender0_twil0)
        self.assertEqual(pobox_id, pobox_id_again)
        self.assertIsNone(connects.connect_viewer(sender0, 'some wrong twilio number'))
        sender0_viewer_data = saveget.get_viewer_data(pobox_id)
        self.assertIn(Sender0.mobile, sender0_viewer_data)
        display_sender(Sender0.mobile, 'sender0 after sender0 sets a viewer for twil0')
        display_postal(pobox_id, 'postbox and view_data after sender0 sets a viewer for twil0')

        # Sender0 sends another card. This appears in the pobox, but not yet in viewer_data.
        # The pobox is updated on each new card, but viewer_data updates only on creation or on some viewer refresh
        cmds.interpret_one_cmd(Sender0.newpostcard_haveviewer('twil0'))
        sender0 = saveget.get_sender(Sender0.mobile)
        sender0_second_card_id = sender0['conn'][sender0_twil0]['recent_card_id']
        pobox = saveget.get_pobox(pobox_id)
        self.assertNotEqual(sender0_first_card_id, sender0_second_card_id)
        self.assertIn(sender0_first_card_id, pobox['cardlists'][Sender0.mobile])
        self.assertIn(sender0_second_card_id, pobox['cardlists'][Sender0.mobile])
        display_sender(Sender0.mobile, f'sender0 after setting up a viewer and sending a second card')
        display_postal(pobox_id, f'pobox after sender0 sent that second card')

        # Sender0 connects Sender1 to the viewer:
        # First make the connector, checking msg back
        cmds.interpret_one_cmd(Sender1.connector('twil0'))
        sender1_passkey, to_tel_used = connects.get_passkey(Sender1.mobile)
        self.assertEqual(to_tel_used, sender1_twil0)
        self.assertEqual(sender1['conn'][connects]['pobox_id'], None)        # sender1 set no viewer, and sender0 hasn't issued the connect

        # Issue the connect command and inspect the results
        sender0_msg_back = cmds.interpret_one_cmd(Sender0.connect('twil0', Sender1.mobile, sender1_passkey))
        sender1 = saveget.get_sender(Sender1.mobile)
        self.assertEqual(sender0_msg_back, 'Successful connect message')
        self.assertEqual(sender1['conn'][sender1_twil0]['pobox_id'], pobox_id)    # Now, sender1 has a pobox_id associated with the connection
        self.assertEqual(sender1['conn'][connects]['pobox_id'], sender0['conn'][sender0_twil0]['pobox_id'])

        display_sender(Sender0.mobile, 'sender0 after sender0 connects sender1 to his postbox')
        display_sender(Sender1.mobile, 'sender1 after sender0 connects sender1 to his postbox')
        display_postal(pobox_id, 'postbox and view_data after sender0 connects sender1. sender1 has not yet sent a card.')

        # sender1 now sends a card to the new connection. This will appear in pobox but not yet viewer_data
        Sender1.newpostcard_haveviewer('twil0')
        sender1 = saveget.get_sender(Sender1.mobile)
        sender1_recent_card_id = sender1['conn'][sender1_twil0]['recent_card_id']
        pobox = saveget.get_pobox(pobox_id)
        self.assertIn(sender1_recent_card_id, pobox['cardlists'][Sender1.mobile])
        # This display wanting to debug: postcard seems to be missing from the pobox!
        display_sender(Sender1.mobile, f'sender1 just sent a card.  Does the pobox show recent card {sender1_recent_card_id} ??')
        display_postal(pobox_id, f'sender1 just sent a card.  Does the pobox show recent card {sender1_recent_card_id} ??')





        # # Sender1 sets up a to: name for a first recipient
        # res0 = cmds.interpret_one_cmd(Sender1.set_to('twil0', 'grammie'))
        # self.assertEqual(res0, 'Renamed recipient kith or kin to grammie')
        # # Sender1 sets up a from: name for himself
        # res1 = cmds.interpret_one_cmd(Sender1.set_from('twil0', 'sonny'))
        # self.assertIn(' identified to others in your sending group by sonny ', res1)
        # # Sender1 changes its profile
        # res2 = cmds.interpret_one_cmd(Sender1.set_profile('twil0', 'new-profile-url'))
        # self.assertEqual(res2, 'OK, your profile image has been updated.')
        # display_sender(Sender0.mobile)
        # display_sender(Sender1.mobile)
        # display_postal(pobox_id)

        # # Sender1 now sends a card to the new connexction
