# postmaster data dictionary

"""
f'sender/{from_tel}':
    # {sender data structure}
    # conn?
    # most recent card (for each to_tel?)

f'conn/{from_tel}/{to_tel}':
    pobox_uuid or None                          # None until viewer is connected for (from_tel, to_tel). 


f'pobox_{pobox_uuid}':
    key_operator: f'{from_tel}              # set when viewer is first connected for (from_tel, to_tel)
    f'{from_tel}:   [postcard_uuid,]        # for each from_tel, a list of postcards not yet archived
    ...

f'card_{postcard_uuid}':
    # {postcard data structure}

    
f'keys_{from_tel}':
    key -> value, expire -> time.time of expiration

"""