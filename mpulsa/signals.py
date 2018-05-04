from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

import requests, json

from .models import Product, Transaksi, ResponseTransaksi
from userprofile.models import PembukuanTransaksi


@receiver(pre_save, sender=Product)
def generate_prod_code(sender, instance, **kwars):
    if instance.kode_internal is None or instance.kode_internal == '':
        instance.kode_internal = '{}{}'.format(instance.operator.kode, int(instance.nominal/1000))



@receiver(post_save, sender=Transaksi)
def note_to_accounttransaction(sender, instance, created, update_fields, **kwargs):
    if created :
        pembukuan_obj = PembukuanTransaksi(
            user = instance.user,
            kredit = instance.price,
            balance = instance.user.profile.saldo - instance.price,
        )
        pembukuan_obj.save()
        instance.pembukuan = pembukuan_obj
        instance.save()

    elif 'status' in update_fields:
        buku_delete = PembukuanTransaksi.objects.filter(transaksi=instance).delete()
        

@receiver(post_save, sender=Transaksi)
def make_transaction_tosb(sender, instance, created, **kwargs):
    if created:
        pord_code = instance.product.kode_external
        phone = instance.phone
        trx_code = instance.trx_code

        data = {
            "opcode": "pulsa",
            "uid": settings.SIAPBAYAR_ID,
            "pin": settings.SIAPBAYAR_PASS,
            "productcode": pord_code,
            "nohp": phone,
            "refca": trx_code
        }

        url = settings.SIAP_URL
        try :
            r = requests.post(url, data=json.dumps(data), headers={'Content-Type':'application/json'})
            rjson = r.json()

            response_trx = ResponseTransaksi.objects.create(
                trx=instance,
                nohp=rjson['nohp'],
                info=rjson['info'],
                product_code=rjson['productcode'],
                trxtime=rjson['trxtime'],
                serial_no=rjson['serialno'],
                price=rjson['price'],
                balance=rjson['balance'],
                refca=rjson['refca'],
                refsb=rjson['refsb'],
                response_code=rjson['rc'],
            )
        except:
            pass
