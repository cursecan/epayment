from django.utils.crypto import get_random_string
from string import digits, ascii_uppercase

def create_code_new(size=10, chars=digits):
    return get_random_string(size, chars)


def generate_code_game_rb_trx(instance, size=10, prefix='04'):
    new_code = prefix + create_code_new(size=size)

    trx_class = instance.__class__
    trx_exists = trx_class.objects.filter(trx_code=new_code).exists()
    if trx_exists:
        return generate_code_trx(instance)

    return new_code