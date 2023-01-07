
import os
import json
import time
import pprint

from django.test import TestCase

from twitalk import new_sender, free_tier
from postoffice import cmds

from . import views as old_filer

data_source = os.environ['POSTBOX_DATA_SOURCE']
wanted_from_tels = ('+16502196500', '+16502185923', '+16508159597', '+12068173605')

pp = pprint.PrettyPrinter(indent=2)

# Get postcards ordered by time.
# Get senders ordered by from_tel
# Get connections ordered by from_tel

# 1. From a list of wanted senders, for each sender, get oldest card and profile and nq the sender.
# 2. Connect the 650.219... to the established pobox_id, adding a key value to do this into connects.connect_viewer
# 3. For each of the others, run connect command by getting passkey in twitalk (doing nq write and read) and...
#       running connect command, sent from free_tier.
#  ==> write this as a functional test, which it is, but produces a useful result. After each step, test and
#       maybe print for inspection.
#       Write all this in test_  !!
#



class OneCmdTests(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_build_one_step_at_a_time(self):
        old_filer.aws_read_bucket_name = 'real-software-bucket'
        all_state = old_filer.load_state_from_s3()
        senders, post_office, cards_in_progress, connections, postal_admin = all_state
        some_cards = old_filer.get_cards(limit=4)
        print('\n')
        print('\nsenders')
        for from_tel in senders:
            print('\n')
            pp.pprint(senders[from_tel])
        print('\n')
        print('\nconnections')
        for from_tel in connections:
            print('\n')
            pp.pprint(connections[from_tel])
        print('\n')
        print(f'got {len(some_cards)}')        
        for a_card in some_cards:
            print('\n')
            pp.pprint(a_card)
