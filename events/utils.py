import random
import string


def token(size=15, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def create_token(instance, size=15):
    new_token = token(size=size)
    EventInviteeClass = instance.__class__
    qs_exists = EventInviteeClass.objects.filter(token=new_token).exists()

    if qs_exists:
        return create_token(size=size)

    return new_token
