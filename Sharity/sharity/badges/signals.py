from django.dispatch import Signal

offer_detail = Signal(providing_args=['owner_pk'])
profile_detail = Signal(providing_args=['owner_pk'])
timeline = Signal(providing_args=['owner_pk'])