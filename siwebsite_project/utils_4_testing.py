class make_sender_values():
    def __init__(self, name, card_number=0):
        self.from_tel = f'{name}__from_tel'
        self.to_tel = f'{name}__to_tel'
        self.profile_url = f'{name}__profile'
        self.image_url = f'{name}__image_{card_number}'
        self.audio_url = f'{name}__audio_{card_number}'
        self.wip = dict(
            image_timestamp = 'image_timestamp', 
            image_url = self.image_url, 
            audio_timestamp =' audio_timestamp', 
            audio_url = self.audio_url
        )

        