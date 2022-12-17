from django.test import TestCase


# make cards and pobox. Test played_it, update update_pobox_new_card.
# Does postmaster test update_pobox_new_card??
# postoffice replaces the old 'read' website completely

from filer import views as filerviews 

from postoffice import test_cmds

class OneCmdTests(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()

    def test_can_do_make_two_sender_viewer_data(self):
        """Makes test data using code from postmaster.test_cmds.  Testing to see if this can be fed to the new postcard viwer code."""
        viewer_data = test_cmds.make_two_sender_viewer_data()
        self.assertIn('meta', viewer_data)




