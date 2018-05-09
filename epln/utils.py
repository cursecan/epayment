from django.utils.crypto import get_random_string
from string import digits, ascii_uppercase

def generate_code(size=10, chars=digits+ascii_uppercase):
    return get_random_string(size, chars)


def generate_pln_trx(instance, size=10, prefix='P2'):
    new_code = prefix + generate_code(size=size)

    trx_class = instance.__class__
    trx_exists = trx_class.objects.filter(trx_code=new_code).exists()
    if trx_exists:
        return generate_pln_trx(instance)
        
    return new_code