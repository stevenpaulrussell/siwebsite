from django.test import TestCase
import time


# make cards and pobox. Test played_it, update update_pobox_new_card.
# Does postmaster test update_pobox_new_card??
# postoffice replaces the old 'read' website completely

from filer import views as filerviews 
from postoffice import event_handler, connects
from postoffice import views as postofficeviews
from saveget import saveget
from siwebsite_project.utils_4_testing import pp, New_Tests_Sender
from . import views


def make_two_sender_viewer_data():
    Sender_0 = New_Tests_Sender()
    Sender_1 = New_Tests_Sender()
    # Sender_0 signs up: first sends a postcard, then a profile (following Twilio prompts). 'twi2' sends the NewSenderFirst message on an AWS queue. 
    event = dict(event_type='new_postcard', wip=Sender_0.new_card_wip(), context='NewSenderFirst', profile_url=Sender_0.profile_url, \
                tel_id=Sender_0.tel_id, svc_id=Sender_0.svc_A, sent_at='sent_at')
    event_handler.interpret_one_event(event)
    # Sender_1 signs up
    event = dict(event_type = 'new_postcard', wip=Sender_1.new_card_wip(), context='NewSenderFirst', profile_url=Sender_1.profile_url, \
                tel_id=Sender_1.tel_id, svc_id=Sender_1.svc_A, sent_at='sent_at')
    event_handler.interpret_one_event(event)

    # Sender_1 sends to a second twilio number
    event = dict(event_type='new_postcard', wip=Sender_1.new_card_wip(), context='NoViewer', profile_url=Sender_1.profile_url, \
                tel_id=Sender_1.tel_id, svc_id=Sender_1.svc_A, sent_at='sent_at')
    event_handler.interpret_one_event(event)

    # Get a viewer for sender0's boxlink (tel_id, svc_id)
    boxlink = saveget.get_boxlink(Sender_0.tel_id, Sender_0.svc_A)
    pobox_id = postofficeviews.new_pobox_id(boxlink)

    # Sender_0 sends another card. This appears in the pobox, but not yet in viewer_data.
    # ====> Note change to context from 'NoViewer' to 'HaveViewer'!  The context sets the logic !!!!!!!!!!
    event = dict(event_type='new_postcard', wip=Sender_0.new_card_wip(), context='HaveViewer', profile_url=Sender_1.profile_url, \
                tel_id=Sender_0.tel_id, svc_id=Sender_0.svc_A, sent_at='sent_at')
    event_handler.interpret_one_event(event)

    # Sender0 connects Sender1 to the viewer:
    PASSKEY = 'pw_1'
    event = dict(event_type='passkey', passkey=PASSKEY, expire=time.time()+10, tel_id=Sender_1.tel_id, svc_id=Sender_1.svc_A)
    response = event_handler.interpret_one_event(event)
    # Issue the connect command and inspect the results
    text = f'connect {Sender_1.tel_id} passkey {PASSKEY}'
    event = dict(event_type='text_was_entered', text=text, tel_id=Sender_0.tel_id, svc_id=Sender_0.svc_A)
    sender0_msg_back = event_handler.interpret_one_event(event)

    # Sender1 now sends a card to the new connection. This will appear in pobox but not yet viewer_data
    event = dict(event_type='new_postcard', wip=Sender_1.new_card_wip(), context='HaveViewer', profile_url=Sender_1.profile_url, \
                tel_id=Sender_1.tel_id, svc_id=Sender_1.svc_A, sent_at='sent_at')
    event_handler.interpret_one_event(event)
    pobox = saveget.get_pobox(pobox_id)
    viewer_data = pobox['viewer_data']
    return viewer_data


class OneCmdTests(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()

    def test_can_do_make_two_sender_viewer_data(self):
        """Makes test data using code from postmaster.test_event_handler.  Testing to see if this can be fed to the new postcard viwer code."""
        viewer_data = make_two_sender_viewer_data()
        print(f'\nline 69 postbox tests, here is viewer_data:')
        pp.pprint(viewer_data)
        self.assertEqual(len(viewer_data), 2)





