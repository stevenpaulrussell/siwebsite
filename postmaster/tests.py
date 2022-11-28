from django.test import TestCase

from filer import views as filerviews 

from twitalk.tests import SiWebCarepostUser

from . import postcards

class Postcard_commands(TestCase):
    def setUp(self):
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()

    def test_create_new_sender(self):
        sender = postcards.create_new_sender('from_tel', 'profile_url')
        self.assertEqual(sender['version'], 1)
        self.assertEqual(sender['conn'], {})

    def test_create_new_connection(self):
        sender = postcards.create_new_sender('a_from_tel', 'profile_url')
        postcards.create_new_connection(sender, 'to_tel')
        conns = sender['conn']
        self.assertEqual(conns['to_tel']['to'], 'kith or kin')
        self.assertEqual(conns['to_tel']['pobox_id'], None)

    def test_make_morsel_no_postbox(self):
        sender = postcards.create_new_sender('a_from_tel', 'profile_url')
        postcards.create_new_connection(sender, 'a_to_tel')
        morsel = postcards.make_morsel(sender)
        self.assertEqual(morsel['a_to_tel']['from'], 'from_tel derived')
        self.assertEqual(morsel['a_to_tel']['to'], 'kith or kin')
        self.assertEqual(morsel['a_to_tel']['have_viewer'], False)
        