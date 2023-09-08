class make_sender_values():
    def __init__(self, name, card_number=0):
        self.tel_id = f'{name}__tel_id'
        self.svc_id = f'{name}__svc_id'
        self.profile_url = f'{name}__profile'
        self.image_url = f'{name}__image_{card_number}'
        self.audio_url = f'{name}__audio_{card_number}'
        self.wip = dict(
            image_timestamp = 'image_timestamp', 
            image_url = self.image_url, 
            audio_timestamp =' audio_timestamp', 
            audio_url = self.audio_url
        )



import time

class New_Tests_Sender():
    """This intended to simplify test by simpler naming and simple methods."""
    last_tel_id_number = 0
    last_card_number = 0

    def __init__(self, svc_id_letter='A'):
        New_Tests_Sender.last_tel_id_number += 1
        self.tel_id = f'+ab{New_Tests_Sender.last_tel_id_number}'
        self.svc_id = f'+{svc_id_letter}'
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




            