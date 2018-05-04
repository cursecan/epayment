from django.utils.crypto import get_random_string

from string import digits

def generate_profile_code(size=5, chars=digits):
    return get_random_string(size, chars)


def get_init_profcode(instance, size=5):
    new_code = generate_profile_code(size)

    profile_class = instance.__class__
    profile_objs = profile_class.objects.filter(token_code=new_code)
    if profile_objs.exists():
        return get_init_profcode(instance)

    return new_code