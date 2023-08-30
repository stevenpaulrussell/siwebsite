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

        