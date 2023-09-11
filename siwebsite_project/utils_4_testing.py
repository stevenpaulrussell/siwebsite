"""Use this to replace sender_object_for_tests, making the tests easier to read."""

import time
import pprint

pp = pprint.PrettyPrinter(indent=2)

class New_Tests_Sender():
    """This intended to simplify test by simpler naming and simple methods."""
    last_tel_id_number = 0
    last_card_number = 0

    def reset():  # Used so tests always start with the same test numbers.
        New_Tests_Sender.last_tel_id_number = 0
        New_Tests_Sender.last_card_number = 0

    def __init__(self):
        New_Tests_Sender.last_tel_id_number += 1
        self.tel_id = f'+..{New_Tests_Sender.last_tel_id_number}'
        self.svc_A = 'svc_A'
        self.svc_B = 'svc_B'
        self.svc_C = 'svc_C'
        self.profile_url = f'{self.tel_id}_profile'

    def new_card_wip(self, now = time.time()):
        New_Tests_Sender.last_card_number += 1
        card_id = f'c_{New_Tests_Sender.last_card_number}'
        return dict(
            image_timestamp = now, 
            image_url = f'c_{card_id}_img', 
            audio_timestamp = now, 
            audio_url = f'c_{card_id}_aud'
        )




            