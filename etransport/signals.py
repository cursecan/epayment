from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

import requests, json
import telepot

from .models import Product, Transaksi, ResponseTransaksi
from userprofile.models import PembukuanTransaksi


@receiver(pre_save, sender=Product)
def generate_prod_code(sender, instance, **kwars):
    if instance.kode_internal is None or instance.kode_internal == '':
        instance.kode_internal = '{}{}'.format(instance.operator.kode, int(instance.nominal/1000))


@receiver(post_save, sender=Transaksi)
def transaction_recording(sender, instance, created, update_fields=[], **kwargs):
    if created :
        # proses pembukuan
        pembukuan_obj = PembukuanTransaksi(
            user = instance.user,
            kredit = instance.price,
            balance = instance.user.profile.saldo - instance.price,
        )
        pembukuan_obj.save()
        instance.pembukuan = pembukuan_obj
        instance.save(update_fields=['pembukuan'])