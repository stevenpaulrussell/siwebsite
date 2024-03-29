"""

Don't test twitalk.  Test 'web backend' and 'web front-end' aka player (?)
using only sqs and urls to drive state.  Examine state with anything.


"""


import time
import json
import os
import requests


from django.test import TestCase

from filer import views as filerviews 
from twitalk.free_tier import mms_to_free_tier
from saveget import saveget
from postoffice import event_handler, connects
from postoffice.views import new_pobox_id, pobox_id_if_good_passkey
from postmaster.views import tickles


from .sender_object_for_tests import TwiSim, pp
from .utils_4_testing import New_Tests_Sender

data_source = os.environ['POSTBOX_DATA_SOURCE']
CMD_URL = filerviews.EVENT_URL


"""
Simulate use.  Sender_0 uses a single svc_id and makes a viewer for recipient KinA.
Sender_1 uses two svc_ids, sending to both KinA and KinB.
Flow:
    Sender_0 signs up using twilio 'svc_A'  
    Sender_1 signs up, also using twilio 'svc_A'
    Sender_1 sends to a second twilio number, 'svc_B'
    Sender_0 gets a passkey, and uses it in a http request to be assigned a postbox_id
    Sender_0 sends a second card
    Sender_1 gets a passkey for his svc_A 'boxlink'. Sender_0 uses the passkey to connect that boxlink to his own pobox.
    Sender_1 sets up a viewer for svc_A, and it is the same view that Sender_0 set up.
    Sender_1 changes his from: id, the recipient to: id, and also his profile image
    Sender_1 senda a card on that connection.
    ==> The other two connections are not exercised in this test.
"""


def display_sender(tel_id, comment=None):
    if comment:
        print('\n\n','='*20)
        print(comment)
    sender = saveget.get_sender(tel_id)
    morsel = filerviews.load_from_free_tier(tel_id)
    print(f'\nsender <{tel_id}>:')
    pp.pprint(sender)

def display_boxlink(boxlink, comment=None):
    if comment:
        print('\n\n','='*20)
        print(comment)
    print(f"\nboxlink <{boxlink['tel_id'], boxlink['svc_id']}>:")
    pp.pprint(boxlink)

def display_postal(pobox_id, comment=None):
    if comment:
        print('\n\n','='*20)
        print(comment)
    pobox = saveget.get_pobox(pobox_id)
    viewer_data = pobox['viewer_data']
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
        # reset New_Tests_Sender
        New_Tests_Sender.reset()

    def test_backend_using_simulation_of_two_senders(self):
        # Show reminder message
        print(f'\n====> lines displaying state in test_functional are commented out.  Change for inspection!\n')

        Sender_0 = New_Tests_Sender()
        Sender_1 = New_Tests_Sender()
        def get_2_senders():
            return saveget.get_sender(Sender_0.tel_id), saveget.get_sender(Sender_1.tel_id)
        def get_3_corresponds():
            boxlink0toA = saveget.get_boxlink(Sender_0.tel_id, Sender_0.svc_A)
            boxlink1toA = saveget.get_boxlink(Sender_1.tel_id, Sender_1.svc_A)
            boxlink1toB = saveget.get_boxlink(Sender_1.tel_id, Sender_1.svc_B)
            return boxlink0toA, boxlink1toA, boxlink1toB
        
        # Sender_0 signs up: first sends a postcard, then a profile (following Twilio prompts). 'twi2' sends the NewSenderFirst message on an AWS queue. 
        msg0 = dict(wip=Sender_0.new_card_wip(), context='NewSenderFirst', profile_url=Sender_0.profile_url, \
                    tel_id=Sender_0.tel_id, svc_id=Sender_0.svc_A, sent_at='sent_at', event_type='new_postcard')
        filerviews.send_an_sqs_message(msg0, CMD_URL)
        # Sender_1 signs up
        msg1 = dict(wip=Sender_1.new_card_wip(), context='NewSenderFirst', profile_url=Sender_1.profile_url, \
                    tel_id=Sender_1.tel_id, svc_id=Sender_1.svc_A, sent_at='sent_at', event_type='new_postcard')
        filerviews.send_an_sqs_message(msg1, CMD_URL)
        # Message processing is started asynchronously
        http_response = tickles('request_dummy')
        # Get the results....
        boxlink0toA = saveget.get_boxlink(Sender_0.tel_id, Sender_0.svc_A)
        boxlink1toA = saveget.get_boxlink(Sender_1.tel_id, Sender_1.svc_A)
        sender0_card_in_play, sender0_unplayed_queue = boxlink0toA['card_current'], boxlink0toA['cardlist_unplayed']
        sender1_unplayed_queue = boxlink1toA['cardlist_unplayed']
        events_admins_msgs = json.loads(http_response.content)
        cmd_msgs, admin_msgs = events_admins_msgs['cmd_msgs'], events_admins_msgs['admin_msgs']
        # Test the results
        self.assertEqual('new_postcard', cmd_msgs[1]['event_type'])     # Telemetry
        self.assertIn('using new svc_id', admin_msgs[1])                # Telemetry
        self.assertEqual(len(sender0_unplayed_queue), 1)
        self.assertEqual(len(sender1_unplayed_queue), 1)
        self.assertIsNone(sender0_card_in_play)       # A card sent remains in the unplayed queue until a viewer is established
        # Check the card contents
        sender1_first_card_id = sender1_unplayed_queue[0]
        sender1_first_card = saveget.get_postcard(sender1_first_card_id)
        self.assertEqual(sender1_first_card['tel_id'], (Sender_1.tel_id))

        # Sender_1 sends to a second twilio number. twi2 notices the first use of that number by this sender
        msg1 = dict(wip=Sender_1.new_card_wip(), context='NewRecipientFirst', profile_url=Sender_1.profile_url, \
                    tel_id=Sender_1.tel_id, svc_id=Sender_1.svc_B, sent_at='sent_at', event_type='new_postcard')
        filerviews.send_an_sqs_message(msg1, CMD_URL)
        # Sender1 sends a second card to the first twilio number. twi2 again notices the context
        msg1 = dict(wip=Sender_1.new_card_wip(), context='NoViewer', profile_url=Sender_1.profile_url, \
                    tel_id=Sender_1.tel_id, svc_id=Sender_1.svc_A, sent_at='sent_at', event_type='new_postcard')
        filerviews.send_an_sqs_message(msg1, CMD_URL)
        tickles('request_dummy')
        # Check that all is as expected: No viewer, 3 cards sent, each on a different (tel_id, svc_id) pair, a 'boxlink'
        # The morsel that is part of sender records the existence of these, and the content for now is only each boxlink.
        sender0, sender1 = get_2_senders()
        sender1_morsel = sender1['morsel']
        sender1_profile = sender1['profile_url']
        boxlink0toA, boxlink1toA, boxlink1toB = get_3_corresponds()  
        self.assertEqual(len(boxlink1toB['cardlist_unplayed']), 1)  # Now have the 3 boxlink, each with a card in the wait queue -- cardlist_unplayed
        self.assertEqual(sender1_profile, '+..2_profile')
        self.assertEqual(sender1_morsel[Sender_1.svc_A]['recipient_moniker'], 'kith or kin')
        self.assertEqual(sender1_morsel[Sender_1.svc_B]['have_viewer'], False)
        display_sender(Sender_0.tel_id, 'sender_0 before setting any viewer')
        display_sender(Sender_1.tel_id, 'sender_1, two recipients, before setting any viewer')
        display_boxlink(boxlink1toA, 'sender_1 first boxlink')

        # Sender_0 gets a passkey to enable making a viewer for 'KinA'.  
        sender0_passkey_msg = mms_to_free_tier(time.time(), Sender_0.tel_id, Sender_0.svc_A, 'passkey', None, None)    # nq_sqs happens 
        sender0_passkey =  sender0_passkey_msg.split('"')[1]
        # To use the passkey, postmaster must be tickled!  Manual now, might change so that pobox search fires off a tickle first!
        http_response = tickles('request_dummy')

        # Now postoffice side works, it would not without the tickle  This sets up the pobox, returning pobox_id.  
        # In this test script, the request is redirected to the player, and that updates viewer data from the poboc
        redirect_response = requests.post(f'{data_source}/get_a_pobox_id', data={'tel_id': Sender_0.tel_id, 'passkey': sender0_passkey})
        redirected_url = redirect_response.url
        # Needed @csrf_exempt in the code so that post gets a status code 200 not 403, and returns the json encoded viewer_data
        response2 = requests.post(redirected_url)
        KinA_postbox_id =  redirected_url.split('/postbox/')[-1]
        pobox_id_again = pobox_id_if_good_passkey(Sender_0.tel_id, sender0_passkey)
        KinA_pobox = saveget.get_pobox(KinA_postbox_id)
        KinA_viewer_data = KinA_pobox['viewer_data']
        KinA_sender0_viewer_data = KinA_viewer_data[Sender_0.tel_id]

        # And check the results
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(KinA_postbox_id, pobox_id_again)
        self.assertIsNone(pobox_id_if_good_passkey(Sender_0.tel_id, 'some wrong twilio number'))
        self.assertIn(Sender_0.tel_id, KinA_viewer_data)
        self.assertEqual(KinA_sender0_viewer_data['profile_url'], Sender_0.profile_url)

        # Sender_0 sends a second card, which appears in the pobox, but not yet in viewer_data.
        msg0 = dict(wip=Sender_0.new_card_wip(), context='HaveViewer', \
                    tel_id=Sender_0.tel_id, svc_id=Sender_0.svc_A, sent_at='sent_at', event_type='new_postcard')
        filerviews.send_an_sqs_message(msg0, CMD_URL)
        tickles('request_dummy')
        boxlink0toA = saveget.get_boxlink(Sender_0.tel_id, Sender_0.svc_A)
        sender0_first_card_id = boxlink0toA['card_current']
        sender0_second_card_id = boxlink0toA['cardlist_unplayed'][0]
        sender0_pobox_id = boxlink0toA['pobox_id']
        pobox = saveget.get_pobox(sender0_pobox_id)
        # Check the results.  
        self.assertIn(sender0_second_card_id, boxlink0toA['cardlist_unplayed'])

        # updating viewer_data changes nothing becaue the card in viewer_data remains unplayed
        # update_viewer_data(pobox, sender0_viewer_data)
        secondcard_pobox = saveget.get_pobox(sender0_pobox_id)
        secondcard_viewer_data = secondcard_pobox['viewer_data']
        self.assertEqual(sender0_first_card_id, secondcard_viewer_data[Sender_0.tel_id]['card_id'])
        self.assertNotEqual(sender0_second_card_id, secondcard_viewer_data[Sender_0.tel_id]['card_id'])

        # display_sender(Sender0.mobile, f'sender0 after setting up a viewer and sending a second card')
        # display_postal(sender0_postbox_id, f'pobox after sender0 sent that second card')

        # Sender_0 connects Sender_1 to the viewer, using a passkey supplied by Sender_1 for svc_A
        sender1_passkey_msg = mms_to_free_tier(time.time(), Sender_1.tel_id, Sender_1.svc_A, 'passkey', None, None)   # nq_sqs happens 
        sender1_passkey =  sender1_passkey_msg.split('"')[1]
        # To use the passkey, postmaster must be tickled!  Manual now, might change so that pobox search fires off a tickle first!
        http_response = tickles('request_dummy')
        # Issue the connect command and inspect the results
        cmd = f'connect {Sender_1.tel_id} passkey {sender1_passkey}'
        sender0_msg_back = mms_to_free_tier(time.time(), Sender_0.tel_id, Sender_0.svc_A, cmd, None, None)   # nq_sqs happens 
        self.assertIn(f'Your command <{cmd}> is queued for processing', sender0_msg_back)
        tickles('request_dummy')  # again, tickle needed from some source to get the postmaster side to notice the changes
        boxlink0toA, boxlink1toA, boxlink1toB = get_3_corresponds()      
        self.assertEqual(boxlink1toA['pobox_id'], sender0_pobox_id)    # Now, sender1 has a pobox_id associated with the connection
        self.assertEqual(boxlink1toA['pobox_id'], boxlink0toA['pobox_id'])

        # display_sender(Sender0.mobile, 'sender0 after sender0 connects sender1 to his postbox --- no change to sender0')
        # display_sender(Sender1.mobile, 'sender1 after sender0 connects sender1 to his postbox. Note the change to pobox_id')
        # display_postal(sender0_postbox_id, 'postbox and view_data after sender0 connects sender1. sender1 has not yet sent a card.')

        # Sender1 does his viewer setup, and gets the same url as Sender0 had:  No need to do the connection, but one can! 
        sender1 = saveget.get_sender(Sender_1.tel_id)
        sender1_passkey_msg = mms_to_free_tier(time.time(), Sender_1.tel_id, Sender_1.svc_A, 'passkey', None, None)    # nq_sqs happens 
        sender1_passkey =  sender1_passkey_msg.split('"')[1]

        # To use the passkey, postmaster must be tickled!  Manual now, might change so that pobox search fires off a tickle first!
        tickles('request_dummy')
        sender1_redirect_response = requests.post(f'{data_source}/get_a_pobox_id', data={'tel_id': Sender_1.tel_id, 'passkey': sender1_passkey})
        sender1_redirected_url = sender1_redirect_response.url
        self.assertEqual(redirected_url, sender1_redirected_url)

        # Sender1 sets up a to: name for a first recipient
        sender1_to_back = mms_to_free_tier(time.time(), Sender_1.tel_id, Sender_1.svc_A, 'to: grammie', None, None)   # nq_sqs happens 
        # Sender1 sets up a from: name for himself
        sender1_from_back = mms_to_free_tier(time.time(), Sender_1.tel_id, Sender_1.svc_A, 'from: sonny', None, None)   # nq_sqs happens 
        # Sender1 changes its profile
        sender1_profile_back = mms_to_free_tier(time.time(), Sender_1.tel_id, Sender_1.svc_A, 'profile', 'new-profile-url', None)   # nq_sqs happens 
        self.assertIn('Your command <to: grammie> is queued for processing', sender1_to_back)
        self.assertIn('Your command <from: sonny> is queued for processing', sender1_from_back)
        self.assertEqual(sender1_profile_back, 'Your profile will be updated shortly, and you will be notified.')

        # display_sender(Sender1.mobile, 'sender1 after setting from: and to: names, and changing profile.')
        # display_postal(sender0_postbox_id, 'pobox shows no change from sender1 setting to, from, and profile. Profile changes with new card.')

        # Sender1 now sends a card to the new connection. This will appear in connection but not yet viewer_data
        msg1 = dict(wip=Sender_1.new_card_wip(), context='HaveViewer', \
                    tel_id=Sender_0.tel_id, svc_id=Sender_0.svc_A, sent_at='sent_at', event_type='new_postcard')
        filerviews.send_an_sqs_message(msg1, CMD_URL)
        tickles('request_dummy') 
        boxlink0toA, boxlink1toA, boxlink1toB = get_3_corresponds()    
        sender0_postbox_id = boxlink1toA['pobox_id']  
        sender1_recent_card_id = boxlink1toA['cardlist_unplayed'][-1]


        pobox = saveget.get_pobox(sender0_postbox_id)
        viewer_data = pobox['viewer_data']

        # Below used to say NotIn, because the update of viewer_data did not occur when with a new card.  But, check all this and complete the test!
        self.assertIn(Sender_1.tel_id, viewer_data)


        # Played it???????????????????????/


        response = requests.post(sender1_redirected_url)
        self.assertEqual(response.status_code, 200)


        sender1_postbox_id =  sender1_redirected_url.split('/postbox/')[-1]        
        pobox = saveget.get_pobox(sender1_postbox_id)
        viewer_data = pobox['viewer_data']

        print(f"What is to be checked with the new logic, line 264?? Here is viewer_data:\n{viewer_data}\n")


        self.assertIn(Sender_0.tel_id, viewer_data)
        self.assertIn(Sender_1.tel_id, viewer_data)

        display_boxlink(boxlink0toA, 'Ending sender_0  boxlink')
        display_boxlink(boxlink1toA, 'Ending sender_1 first boxlink')
        display_boxlink(boxlink1toB, 'Ending sender_1 second boxlink')


        # display_postal(pobox_id, f'sender1 just sent a card.  This appears in the pobox, and viewer_data shows the changed profile')

        self.assertFalse('connect command needs to check whether the issuer is the key_operator.  Make unit and functional tests for this case.')

        self.assertFalse('Still need to check on this last part, and see if the test on played it and new cards is here.  Almost done!')
        self.assertFalse('Need to make the process to archive cards and move media!')



    def xtest_frontend_using_simulation_of_two_senders(self):
        # Set up as in test_backend..... but not doing any checks on the results
        Sender0 = TwiSim('Mr0')
        Sender1 = TwiSim('Ms1')
        sender1_twil0 = Sender1.twi_directory['twil0']
        sender1_twil1 = Sender1.twi_directory['twil1']
        sender0_twil0 = Sender0.twi_directory['twil0']
        
        # Sender0 and Sender1 sign up, neither has a viewer yet. Nothing new being tested here
        event_handler.interpret_one_event(Sender0.newsender_firstpostcard())
        event_handler.interpret_one_event(Sender1.newsender_firstpostcard())

        # Sender1 sends to a second twilio number
        event_handler.interpret_one_event(Sender1.newrecipient_postcard('twil1'))

        # Sender1 sends a second card to the first twilio number
        event_handler.interpret_one_event(Sender1.newpostcard_noviewer('twil0'))
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
        event_handler.interpret_one_event(Sender0.newpostcard_haveviewer('twil0'))
        sender0 = saveget.get_sender(Sender0.mobile)
        sender0_second_card_id = sender0['conn'][sender0_twil0]['recent_card_id']
        pobox = saveget.get_pobox(pobox_id)

        # Sender0 connects Sender1 to the viewer:
        # First make the passkey, checking msg back
        event_handler.interpret_one_event(Sender1.passkey('twil0'))
        sender1_passkey, svc_id_used = connects.get_passkey(Sender1.mobile)

        # Issue the connect command and inspect the results
        sender0_msg_back = event_handler.interpret_one_event(Sender0.connect('twil0', Sender1.mobile, sender1_passkey))
        sender1 = saveget.get_sender(Sender1.mobile)

        # Sender1 sets up a to: name for a first recipient
        res0 = event_handler.interpret_one_event(Sender1.set_to('twil0', 'grammie'))

        # Sender1 sets up a from: name for himself
        res1 = event_handler.interpret_one_event(Sender1.set_from('twil0', 'sonny'))

        # Sender1 changes its profile
        res2 = event_handler.interpret_one_event(Sender1.set_profile('twil0', 'new-profile-url'))

        # Sender1 now sends a card to the new connection. This will appear in pobox but not yet viewer_data
        event_handler.interpret_one_event(Sender1.newpostcard_haveviewer('twil0'))
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
        response = pobox_id_if_good_passkey(request=None, tel_id=Sender0.mobile, passkey=passkey)
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
    event_handler.interpret_one_event(Sender0.newsender_firstpostcard())
    event_handler.interpret_one_event(Sender1.newsender_firstpostcard())

    # Sender1 sends to a second twilio number
    event_handler.interpret_one_event(Sender1.newrecipient_postcard('twil1'))

    # Sender1 sends a second card to the first twilio number
    event_handler.interpret_one_event(Sender1.newpostcard_noviewer('twil0'))
    # Sender0 makes a viewer.  This sets up the pobox, returning pobox_id.  Viewer_data is initialized with meta only
    sender0 = saveget.get_sender(Sender0.mobile)
    boxlink0A = saveget.get_boxlink(Sender0.mobile, sender0_twil0)
    pobox_id       = new_pobox_id(boxlink0A)
 
    # postbox.update_viewer_data  puts a card in viewer_data
    pobox = saveget.get_pobox(pobox_id)
    updated_viewer_data = pobox['viewer_data']

    # Sender0 sends another card. This appears in the pobox, but not yet in viewer_data.
    event_handler.interpret_one_event(Sender0.newpostcard_haveviewer('twil0'))
    pobox = saveget.get_pobox(pobox_id)

    # Sender0 connects Sender1 to the viewer:
    # First make the passkey, checking msg back
    event_handler.interpret_one_event(Sender1.passkey('twil0'))
    sender1_passkey, svc_id_used = connects.get_passkey(Sender1.mobile)

    # Issue the connect command and inspect the results
    sender0_msg_back = event_handler.interpret_one_event(Sender0.connect('twil0', Sender1.mobile, sender1_passkey))
    sender1 = saveget.get_sender(Sender1.mobile)

    # Sender1 sets up a to: name for a first recipient
    res0 = event_handler.interpret_one_event(Sender1.set_to('twil0', 'grammie'))

    # Sender1 sets up a from: name for himself
    res1 = event_handler.interpret_one_event(Sender1.set_from('twil0', 'sonny'))

    # Sender1 changes its profile
    res2 = event_handler.interpret_one_event(Sender1.set_profile('twil0', 'new-profile-url'))

    # Sender1 now sends a card to the new connection. This will appear in pobox but not yet viewer_data
    event_handler.interpret_one_event(Sender1.newpostcard_haveviewer('twil0'))

    return Sender0, Sender1
