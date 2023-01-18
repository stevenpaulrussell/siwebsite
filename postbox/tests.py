from django.test import TestCase


# make cards and pobox. Test played_it, update update_pobox_new_card.
# Does postmaster test update_pobox_new_card??
# postoffice replaces the old 'read' website completely

from filer import views as filerviews 
from postoffice import cmds, connects
from postoffice import views as postofficeviews
from saveget import saveget
from siwebsite_project.sender_object_for_tests import TwiSim, pp
from . import views


def make_two_sender_viewer_data():
    Sender0 = TwiSim('Mr0')
    Sender1 = TwiSim('Ms1')
    sender1_twil0 = Sender1.twi_directory['twil0']
    sender1_twil1 = Sender1.twi_directory['twil1']
    sender0_twil0 = Sender0.twi_directory['twil0']

    cmds.interpret_one_cmd(Sender0.newsender_firstpostcard())
    cmds.interpret_one_cmd(Sender1.newsender_firstpostcard())
    # Sender1 sends to a second twilio number
    cmds.interpret_one_cmd(Sender1.newrecipient_postcard('twil1'))

    # Sender0 makes a viewer.  This sets up the pobox, the viewer_data, putting a card in viewer_data, returning pobox_id
    sender0 = saveget.get_sender(Sender0.mobile)
    pobox_id = postofficeviews.new_pobox_id(sender0, sender0_twil0)
    # Sender0 sends another card. This appears in the pobox, but not yet in viewer_data.
    cmds.interpret_one_cmd(Sender0.newpostcard_haveviewer('twil0'))

    # Sender0 connects Sender1 to the viewer:
    cmds.interpret_one_cmd(Sender1.passkey('twil0'))
    sender1_passkey, to_tel_used = connects.get_passkey(Sender1.mobile)
    # Issue the connect command and inspect the results
    sender0_msg_back = cmds.interpret_one_cmd(Sender0.connect('twil0', Sender1.mobile, sender1_passkey))

    # Sender1 now sends a card to the new connection. This will appear in pobox but not yet viewer_data
    cmds.interpret_one_cmd(Sender1.newpostcard_haveviewer('twil0'))
    pobox = saveget.get_pobox(pobox_id)
    viewer_data = saveget.get_viewer_data(pobox_id)
    views.update_viewer_data(pobox, viewer_data)
    return viewer_data


class OneCmdTests(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()

    def test_can_do_make_two_sender_viewer_data(self):
        """Makes test data using code from postmaster.test_cmds.  Testing to see if this can be fed to the new postcard viwer code."""
        viewer_data = make_two_sender_viewer_data()
        self.assertIn('meta', viewer_data)
        pp.pprint(viewer_data)




