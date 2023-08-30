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

class MintaSender():
    def __init__(self, tel_id_number='1', svc_id_letter='A'):
        self.tel_id = f'+{tel_id_number}'
        self.svc_id = f'+{svc_id_letter}'
        self.profile_url = f'{tel_id_number}_pro'
        self.sender_moniker = self.tel_id

            