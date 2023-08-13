import time
import uuid
import pprint
import json
import os
import requests


from django.test import TestCase

from filer import views as filerviews 
from saveget import saveget
from postoffice import cmds, connects
from postbox.views import update_viewer_data, pobox_id_if_good_passkey
from postmaster.views import tickles, get_a_pobox_id

from .sender_object_for_tests import TwiSim, pp
data_source = os.environ['POSTBOX_DATA_SOURCE']

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

    def test_backend_using_simulation_of_two_senders(self):
        # Remember useful constants
        Sender0 = TwiSim('Mr0')
        Sender1 = TwiSim('Ms1')
        sender1_twil0 = Sender1.twi_directory['twil0']
        sender1_twil1 = Sender1.twi_directory['twil1']
        sender0_twil0 = Sender0.twi_directory['twil0']

        # Twilio side is quiet until the sender succeeds in 'sign-up' by making wip and a profile.
        # Sender0 and Sender1 sign up, neither has a viewer yet. Nothing new being tested here
        cmds.interpret_one_event(Sender0.newsender_firstpostcard())
        cmds.interpret_one_event(Sender1.newsender_firstpostcard())
        # Sender1 sends to a second twilio number
        cmds.interpret_one_event(Sender1.newrecipient_postcard('twil1'))
        # Sender1 sends a second card to the first twilio number
        cmds.interpret_one_event(Sender1.newpostcard_noviewer('twil0'))
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

        # Sender0 makes a viewer.  This sets up the pobox, returning pobox_id.  Viewer_data is initialized with meta only
        # Check that, and see that pobox_id is retrieved on a re-look, and that bad values give None
        sender0 = saveget.get_sender(Sender0.mobile)
        pobox_id       = connects.connect_viewer(sender0, sender0_twil0)
        pobox_id_again = connects.connect_viewer(sender0, sender0_twil0)
        self.assertEqual(pobox_id, pobox_id_again)
        self.assertIsNone(connects.connect_viewer(sender0, 'some wrong twilio number'))
        sender0_viewer_data = saveget.get_viewer_data(pobox_id)
        self.assertNotIn(Sender0.mobile, sender0_viewer_data)
        self.assertIn('meta', sender0_viewer_data)
        self.assertEqual(sender0_viewer_data['meta']['pobox_id'], pobox_id)

        # postbox.update_viewer_data removes a card from pobox, putting it in viewer_data
        # The pobox is updated on each new card, but viewer_data updates only on some viewer refresh
        pobox = saveget.get_pobox(pobox_id)
        self.assertIn(sender0_first_card_id, pobox['cardlists'][Sender0.mobile])
        update_viewer_data(pobox, sender0_viewer_data)
        updated_viewer_data = saveget.get_viewer_data(pobox_id)
        self.assertIn(Sender0.mobile, sender0_viewer_data)
        self.assertNotIn(sender0_first_card_id, pobox['cardlists'][Sender0.mobile])
        self.assertEqual(updated_viewer_data[Sender0.mobile]['card_id'], sender0_first_card_id)      # the card is present
        display_sender(Sender0.mobile, 'sender0 after sender0 sets a viewer for twil0')
        display_postal(pobox_id, 'postbox and view_data after sender0 sets a viewer for twil0')

        # Sender0 sends a second card, which appears in the pobox, but not yet in viewer_data.
        cmds.interpret_one_event(Sender0.newpostcard_haveviewer('twil0'))
        sender0 = saveget.get_sender(Sender0.mobile)
        sender0_second_card_id = sender0['conn'][sender0_twil0]['recent_card_id']
        pobox = saveget.get_pobox(pobox_id)
        self.assertNotEqual(sender0_first_card_id, sender0_second_card_id)
        self.assertIn(sender0_second_card_id, pobox['cardlists'][Sender0.mobile])
        # updating viewer_data changes nothing becaue the card in viewer_data remains unplayed
        update_viewer_data(pobox, sender0_viewer_data)
        secondcard_pobox = saveget.get_pobox(pobox_id)
        secondcard_viewer_data = saveget.get_viewer_data(pobox_id)
        self.assertIn(sender0_second_card_id, secondcard_pobox['cardlists'][Sender0.mobile])
        self.assertIn(sender0_first_card_id, secondcard_viewer_data[Sender0.mobile]['card_id'])
        self.assertNotIn(sender0_second_card_id, secondcard_viewer_data[Sender0.mobile]['card_id'])

        display_sender(Sender0.mobile, f'sender0 after setting up a viewer and sending a second card')
        display_postal(pobox_id, f'pobox after sender0 sent that second card')

        # Sender0 connects Sender1 to the viewer:
        # First make the passkey, checking msg back
        cmds.interpret_one_event(Sender1.passkey('twil0'))
        sender1_passkey, to_tel_used = connects.get_passkey(Sender1.mobile)
        self.assertEqual(to_tel_used, sender1_twil0)
        self.assertEqual(sender1['conn'][sender1_twil0]['pobox_id'], None)        # sender1 set no viewer, and sender0 hasn't issued the connect

        # Issue the connect command and inspect the results
        sender0_msg_back = cmds.interpret_one_event(Sender0.connect('twil0', Sender1.mobile, sender1_passkey))
        sender1 = saveget.get_sender(Sender1.mobile)
        self.assertEqual(sender0_msg_back, 'Successfully connected mobile_Ms1 to kith or kin')
        self.assertEqual(sender1['conn'][sender1_twil0]['pobox_id'], pobox_id)    # Now, sender1 has a pobox_id associated with the connection
        self.assertEqual(sender1['conn'][sender1_twil0]['pobox_id'], sender0['conn'][sender0_twil0]['pobox_id'])

        display_sender(Sender0.mobile, 'sender0 after sender0 connects sender1 to his postbox --- no change to sender0')
        display_sender(Sender1.mobile, 'sender1 after sender0 connects sender1 to his postbox. Note the change to pobox_id')
        display_postal(pobox_id, 'postbox and view_data after sender0 connects sender1. sender1 has not yet sent a card.')

        # Sender1 sets up a to: name for a first recipient
        res0 = cmds.interpret_one_event(Sender1.set_to('twil0', 'grammie'))
        self.assertEqual(res0, 'Renamed recipient kith or kin to grammie')
        # Sender1 sets up a from: name for himself
        res1 = cmds.interpret_one_event(Sender1.set_from('twil0', 'sonny'))
        self.assertIn(' identified to others in your sending group by sonny ', res1)
        # Sender1 changes its profile
        res2 = cmds.interpret_one_event(Sender1.set_profile('twil0', 'new-profile-url'))
        self.assertEqual(res2, 'OK, your profile image has been updated.')

        display_sender(Sender1.mobile, 'sender1 after setting from: and to: names, and changing profile.')
        display_postal(pobox_id, 'pobox shows no change from sender1 setting to, from, and profile. Profile changes with new card.')

        # Sender1 now sends a card to the new connection. This will appear in pobox but not yet viewer_data
        cmds.interpret_one_event(Sender1.newpostcard_haveviewer('twil0'))
        sender1 = saveget.get_sender(Sender1.mobile)
        sender1_recent_card_id = sender1['conn'][sender1_twil0]['recent_card_id']
        pobox = saveget.get_pobox(pobox_id)
        viewer_data = saveget.get_viewer_data(pobox_id)
        self.assertEqual(pobox['cardlists'][Sender1.mobile], [sender1_recent_card_id])
        self.assertNotIn(Sender1.mobile, viewer_data)
        # The updated_viewer_data does what it says
        update_viewer_data(pobox, viewer_data)      # changes both pobox and viewer_data, saving both
        pobox = saveget.get_pobox(pobox_id)
        viewer_data = saveget.get_viewer_data(pobox_id)
        self.assertEqual(pobox['cardlists'][Sender1.mobile], [])    # The card is no longer in the list
        self.assertIn(Sender0.mobile, viewer_data)
        self.assertIn(Sender1.mobile, viewer_data)
        display_postal(pobox_id, f'sender1 just sent a card.  This appears in the pobox, and viewer_data shows the changed profile')



    def test_frontend_using_simulation_of_two_senders(self):
        # Set up as in test_backend..... but not doing any checks on the results
        Sender0 = TwiSim('Mr0')
        Sender1 = TwiSim('Ms1')
        sender1_twil0 = Sender1.twi_directory['twil0']
        sender1_twil1 = Sender1.twi_directory['twil1']
        sender0_twil0 = Sender0.twi_directory['twil0']
        
        # Sender0 and Sender1 sign up, neither has a viewer yet. Nothing new being tested here
        cmds.interpret_one_event(Sender0.newsender_firstpostcard())
        cmds.interpret_one_event(Sender1.newsender_firstpostcard())

        # Sender1 sends to a second twilio number
        cmds.interpret_one_event(Sender1.newrecipient_postcard('twil1'))

        # Sender1 sends a second card to the first twilio number
        cmds.interpret_one_event(Sender1.newpostcard_noviewer('twil0'))
        # Sender0 makes a viewer.  This sets up the pobox, returning pobox_id.  Viewer_data is initialized with meta only
        sender0 = saveget.get_sender(Sender0.mobile)
        pobox_id       = connects.connect_viewer(sender0, sender0_twil0)
        sender0_viewer_data = saveget.get_viewer_data(pobox_id)

        # postbox.update_viewer_data  puts a card in viewer_data
        pobox = saveget.get_pobox(pobox_id)
        update_viewer_data(pobox, sender0_viewer_data)
        updated_viewer_data = saveget.get_viewer_data(pobox_id)

        # Sender0 sends another card. This appears in the pobox, but not yet in viewer_data.
        # The pobox is updated on each new card, but viewer_data updates only on some viewer refresh
        cmds.interpret_one_event(Sender0.newpostcard_haveviewer('twil0'))
        sender0 = saveget.get_sender(Sender0.mobile)
        sender0_second_card_id = sender0['conn'][sender0_twil0]['recent_card_id']
        pobox = saveget.get_pobox(pobox_id)

        # Sender0 connects Sender1 to the viewer:
        # First make the passkey, checking msg back
        cmds.interpret_one_event(Sender1.passkey('twil0'))
        sender1_passkey, to_tel_used = connects.get_passkey(Sender1.mobile)

        # Issue the connect command and inspect the results
        sender0_msg_back = cmds.interpret_one_event(Sender0.connect('twil0', Sender1.mobile, sender1_passkey))
        sender1 = saveget.get_sender(Sender1.mobile)

        # Sender1 sets up a to: name for a first recipient
        res0 = cmds.interpret_one_event(Sender1.set_to('twil0', 'grammie'))

        # Sender1 sets up a from: name for himself
        res1 = cmds.interpret_one_event(Sender1.set_from('twil0', 'sonny'))

        # Sender1 changes its profile
        res2 = cmds.interpret_one_event(Sender1.set_profile('twil0', 'new-profile-url'))

        # Sender1 now sends a card to the new connection. This will appear in pobox but not yet viewer_data
        cmds.interpret_one_event(Sender1.newpostcard_haveviewer('twil0'))
        pobox = saveget.get_pobox(pobox_id)
        viewer_data = saveget.get_viewer_data(pobox_id)

        # The updated_viewer_data does what it says
        update_viewer_data(pobox, viewer_data)
        viewer_data = saveget.get_viewer_data(pobox_id)

        # Now run front end tests:
        # Player shows a viewer and works functionally (?)
        # Played it call from viewer updates view_data and pobox etc
        # Check-in from viewer gets a new postcard and updates the heard froms
        # Somebody connects a viewer using webpage....
        # Instructions view works

        # ************************************************************************************
        connects._set_passkey(Sender0.mobile, sender0_twil0)
        passkey = saveget.get_passkey_dictionary(Sender0.mobile)['passkey']
        sender0 = saveget.get_sender(Sender0.mobile)
        expected_pobox_id = sender0['conn'][sender0_twil0]['pobox_id']
        response = pobox_id_if_good_passkey(request=None, from_tel=Sender0.mobile, passkey=passkey)
        got_pobox_id = json.loads(response.content)
        self.assertEqual(expected_pobox_id, got_pobox_id)






def run_simulation_of_two_senders():
    "This runs the scenario to setup a given state but does not test the state.  Used for further testing."
    filerviews.clear_the_read_bucket()
    filerviews.clear_the_sqs_queue_TEST_SQS()
    
    # Set up as in test_backend..... but not doing any checks on the results
    Sender0 = TwiSim('Mr0')
    Sender1 = TwiSim('Ms1')
    sender1_twil0 = Sender1.twi_directory['twil0']
    sender1_twil1 = Sender1.twi_directory['twil1']
    sender0_twil0 = Sender0.twi_directory['twil0']
    
    # Sender0 and Sender1 sign up, neither has a viewer yet. Nothing new being tested here
    cmds.interpret_one_event(Sender0.newsender_firstpostcard())
    cmds.interpret_one_event(Sender1.newsender_firstpostcard())

    # Sender1 sends to a second twilio number
    cmds.interpret_one_event(Sender1.newrecipient_postcard('twil1'))

    # Sender1 sends a second card to the first twilio number
    cmds.interpret_one_event(Sender1.newpostcard_noviewer('twil0'))
    # Sender0 makes a viewer.  This sets up the pobox, returning pobox_id.  Viewer_data is initialized with meta only
    sender0 = saveget.get_sender(Sender0.mobile)
    pobox_id       = connects.connect_viewer(sender0, sender0_twil0)
    sender0_viewer_data = saveget.get_viewer_data(pobox_id)

    # postbox.update_viewer_data  puts a card in viewer_data
    pobox = saveget.get_pobox(pobox_id)
    update_viewer_data(pobox, sender0_viewer_data)
    updated_viewer_data = saveget.get_viewer_data(pobox_id)

    # Sender0 sends another card. This appears in the pobox, but not yet in viewer_data.
    # The pobox is updated on each new card, but viewer_data updates only on some viewer refresh
    cmds.interpret_one_event(Sender0.newpostcard_haveviewer('twil0'))
    sender0 = saveget.get_sender(Sender0.mobile)
    sender0_second_card_id = sender0['conn'][sender0_twil0]['recent_card_id']
    pobox = saveget.get_pobox(pobox_id)

    # Sender0 connects Sender1 to the viewer:
    # First make the passkey, checking msg back
    cmds.interpret_one_event(Sender1.passkey('twil0'))
    sender1_passkey, to_tel_used = connects.get_passkey(Sender1.mobile)

    # Issue the connect command and inspect the results
    sender0_msg_back = cmds.interpret_one_event(Sender0.connect('twil0', Sender1.mobile, sender1_passkey))
    sender1 = saveget.get_sender(Sender1.mobile)

    # Sender1 sets up a to: name for a first recipient
    res0 = cmds.interpret_one_event(Sender1.set_to('twil0', 'grammie'))

    # Sender1 sets up a from: name for himself
    res1 = cmds.interpret_one_event(Sender1.set_from('twil0', 'sonny'))

    # Sender1 changes its profile
    res2 = cmds.interpret_one_event(Sender1.set_profile('twil0', 'new-profile-url'))

    # Sender1 now sends a card to the new connection. This will appear in pobox but not yet viewer_data
    cmds.interpret_one_event(Sender1.newpostcard_haveviewer('twil0'))
    pobox = saveget.get_pobox(pobox_id)
    viewer_data = saveget.get_viewer_data(pobox_id)
    update_viewer_data(pobox, viewer_data)

    return Sender0, Sender1
